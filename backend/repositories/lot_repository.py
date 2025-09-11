"""
Lot Repository - Database operations for lot management
"""

from typing import List, Optional

from config.database import database, get_ist_timestamp
from models.domain.lot import LotRegister


class LotRepository:
    """Lot database operations"""

    def __init__(self):
        self.db_client = database

    async def create_lot(self, lot_data: dict, allocations: List[dict]) -> LotRegister:
        """Create new lot with allocations"""
        client = await self.db_client.get_client()

        # Calculate total pieces from allocations
        total_pieces = sum(allocation["allocated_pieces"] for allocation in allocations)

        # Prepare lot data
        lot_insert_data = {
            "party_id": lot_data["party_id"],
            "quality_id": lot_data["quality_id"],
            "lot_date": str(lot_data.get("lot_date", "")),
            "total_pieces": total_pieces,
            "bill_number": lot_data.get("bill_number"),
            "actual_pieces": lot_data.get("actual_pieces"),
            "delivery_date": str(lot_data.get("delivery_date", ""))
            if lot_data.get("delivery_date")
            else None,
            "notes": lot_data.get("notes"),
            "status": "PENDING",
            "created_at": get_ist_timestamp(),
            "updated_at": get_ist_timestamp(),
        }

        # Create lot
        lot_result = client.table("lot_register").insert(lot_insert_data).execute()
        lot = LotRegister.from_dict(lot_result.data[0])

        # Create allocations
        for allocation in allocations:
            allocation_data = {
                "lot_id": lot.id,
                "order_id": allocation["order_id"],
                "design_number": allocation["design_number"],
                "ground_color_name": allocation["ground_color_name"],
                "beam_color_id": allocation["beam_color_id"],
                "allocated_pieces": allocation["allocated_pieces"],
                "notes": allocation.get("notes"),
                "created_at": get_ist_timestamp(),
                "updated_at": get_ist_timestamp(),
            }
            client.table("lot_allocations").insert(allocation_data).execute()

        return lot

    async def get_lot_by_id(self, lot_id: int) -> Optional[LotRegister]:
        """Get lot by ID"""
        client = await self.db_client.get_client()

        result = (
            client.table("lot_register")
            .select("*")
            .eq("id", lot_id)
            .eq("is_active", True)
            .execute()
        )

        if not result.data:
            return None

        return LotRegister.from_dict(result.data[0])

    async def get_lot_with_details(self, lot_id: int) -> Optional[dict]:
        """Get lot with all details including allocations"""
        client = await self.db_client.get_client()

        # Get lot with party and quality details
        lot_result = (
            client.table("lot_register")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("id", lot_id)
            .eq("is_active", True)
            .execute()
        )

        if not lot_result.data:
            return None

        lot_data = lot_result.data[0]

        # Get allocations with color details
        allocations_result = (
            client.table("lot_allocations")
            .select("""
                *,
                colors!inner(id, color_code, color_name)
            """)
            .eq("lot_id", lot_id)
            .eq("is_active", True)
            .execute()
        )

        # Process allocations
        allocations = []
        for allocation in allocations_result.data:
            allocation_data = {
                **allocation,
                "beam_color_name": allocation["colors"]["color_name"],
                "beam_color_code": allocation["colors"]["color_code"],
            }
            # Remove nested colors data
            del allocation_data["colors"]
            allocations.append(allocation_data)

        # Build complete lot data
        lot_with_details = {
            **lot_data,
            "party_name": lot_data["parties"]["party_name"],
            "quality_name": lot_data["qualities"]["quality_name"],
            "allocations": allocations,
        }

        # Remove nested data
        del lot_with_details["parties"]
        del lot_with_details["qualities"]

        return lot_with_details

    async def get_all_lots(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get all lots with details"""
        client = await self.db_client.get_client()

        # Get lots with party and quality details
        lots_result = (
            client.table("lot_register")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("is_active", True)
            .order("lot_date", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        lots_with_details = []
        for lot_data in lots_result.data:
            # Get allocations for this lot
            allocations_result = (
                client.table("lot_allocations")
                .select("""
                    *,
                    colors!inner(id, color_code, color_name)
                """)
                .eq("lot_id", lot_data["id"])
                .eq("is_active", True)
                .execute()
            )

            # Process allocations
            allocations = []
            for allocation in allocations_result.data:
                allocation_data = {
                    **allocation,
                    "beam_color_name": allocation["colors"]["color_name"],
                    "beam_color_code": allocation["colors"]["color_code"],
                }
                del allocation_data["colors"]
                allocations.append(allocation_data)

            # Build lot data
            lot_with_details = {
                **lot_data,
                "party_name": lot_data["parties"]["party_name"],
                "quality_name": lot_data["qualities"]["quality_name"],
                "allocations": allocations,
            }

            del lot_with_details["parties"]
            del lot_with_details["qualities"]

            lots_with_details.append(lot_with_details)

        return lots_with_details

    async def update_lot(self, lot_id: int, update_data: dict) -> Optional[LotRegister]:
        """Update lot"""
        client = await self.db_client.get_client()

        # Prepare update data
        update_fields = {}
        if "bill_number" in update_data:
            update_fields["bill_number"] = update_data["bill_number"]
        if "actual_pieces" in update_data:
            update_fields["actual_pieces"] = update_data["actual_pieces"]
        if "delivery_date" in update_data:
            update_fields["delivery_date"] = (
                str(update_data["delivery_date"])
                if update_data["delivery_date"]
                else None
            )
        if "status" in update_data:
            update_fields["status"] = update_data["status"]
        if "notes" in update_data:
            update_fields["notes"] = update_data["notes"]

        update_fields["updated_at"] = get_ist_timestamp()

        # Update lot
        result = (
            client.table("lot_register")
            .update(update_fields)
            .eq("id", lot_id)
            .execute()
        )

        if not result.data:
            return None

        return LotRegister.from_dict(result.data[0])

    async def delete_lot(self, lot_id: int) -> bool:
        """Soft delete lot and its allocations"""
        client = await self.db_client.get_client()

        # Soft delete lot
        lot_result = (
            client.table("lot_register")
            .update({"is_active": False, "updated_at": get_ist_timestamp()})
            .eq("id", lot_id)
            .execute()
        )

        # Soft delete allocations
        client.table("lot_allocations").update({"is_active": False}).eq(
            "lot_id", lot_id
        ).execute()

        return bool(lot_result.data)

    async def get_partywise_detail(self, party_id: Optional[int] = None) -> List[dict]:
        """Get partywise detail (red book) data - simplified version"""
        client = await self.db_client.get_client()

        # Get orders with party and quality details
        orders_query = (
            client.table("orders")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("is_active", True)
        )

        if party_id:
            orders_query = orders_query.eq("party_id", party_id)

        orders_result = orders_query.order("order_date", desc=True).execute()

        if not orders_result.data:
            return []

        # Get order items for all orders
        order_ids = [order["id"] for order in orders_result.data]
        items_result = (
            client.table("order_items")
            .select("*")
            .in_("order_id", order_ids)
            .eq("is_active", True)
            .execute()
        )

        # Group items by order
        items_by_order = {}
        for item in items_result.data:
            order_id = item["order_id"]
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append(item)

        # Get existing lot data for these orders (if any lots exist)
        existing_lots_result = (
            client.table("lot_register")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("is_active", True)
            .execute()
        )

        # Get lot allocations
        lot_allocations_result = (
            client.table("lot_allocations").select("*").eq("is_active", True).execute()
        )

        # Create a map of order_id -> lot data for quick lookup
        order_to_lot_map = {}
        for allocation in lot_allocations_result.data:
            order_id = allocation["order_id"]
            if order_id not in order_to_lot_map:
                order_to_lot_map[order_id] = []
            order_to_lot_map[order_id].append(allocation)

        # Build partywise detail data
        partywise_data = []
        for order in orders_result.data:
            order_id = order["id"]
            order_items = items_by_order.get(order_id, [])
            existing_allocations = order_to_lot_map.get(order_id, [])

            # Get all unique design numbers for this order
            all_design_numbers = set()
            for item in order_items:
                if item["design_number"]:
                    if item["design_number"] == "ALL":
                        # For "ALL", generate design numbers based on total_designs
                        design_numbers = [
                            f"D{i + 1:03d}"
                            for i in range(order.get("total_designs", 1))
                        ]
                    else:
                        # Split comma-separated design numbers
                        design_numbers = [
                            d.strip()
                            for d in item["design_number"].split(",")
                            if d.strip()
                        ]
                    all_design_numbers.update(design_numbers)

            # Create a row for each unique design number
            for design_no in sorted(all_design_numbers):
                # Find lot data for this design (check all allocations for this design)
                lot_data = None
                for allocation in existing_allocations:
                    # Check if this allocation matches the design number
                    allocation_designs = []
                    if allocation["design_number"] == "ALL":
                        allocation_designs = [
                            f"D{i + 1:03d}"
                            for i in range(order.get("total_designs", 1))
                        ]
                    else:
                        allocation_designs = [
                            d.strip()
                            for d in allocation["design_number"].split(",")
                            if d.strip()
                        ]

                    if design_no in allocation_designs:
                        # Find the lot for this allocation
                        for lot in existing_lots_result.data:
                            if lot["id"] == allocation["lot_id"]:
                                lot_data = lot
                                break
                        break

                # Get ground color names for this design (comma-separated)
                ground_colors = []
                for item in order_items:
                    item_designs = []
                    if item["design_number"] == "ALL":
                        item_designs = [
                            f"D{i + 1:03d}"
                            for i in range(order.get("total_designs", 1))
                        ]
                    else:
                        item_designs = [
                            d.strip()
                            for d in item["design_number"].split(",")
                            if d.strip()
                        ]

                    if design_no in item_designs:
                        ground_colors.append(item["ground_color_name"])

                ground_color_str = ", ".join(ground_colors)

                partywise_data.append(
                    {
                        "date": order["order_date"],
                        "des_no": design_no,
                        "quality": order["qualities"]["quality_name"],
                        "units_pcs": order["units"],  # Total units for this order
                        "rate": order["rate_per_piece"],
                        "lot_no": lot_data["lot_number"] if lot_data else None,
                        "lot_no_date": lot_data["lot_date"] if lot_data else None,
                        "bill_no": lot_data["bill_number"] if lot_data else None,
                        "actual_pcs": lot_data["actual_pieces"] if lot_data else None,
                        "delivery_date": lot_data["delivery_date"]
                        if lot_data
                        else None,
                        "party_name": order["parties"]["party_name"],
                        "order_id": order_id,
                        "ground_color_name": ground_color_str,
                    }
                )

        return partywise_data

    async def get_lot_register(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get lot register data - shows all orders with each design as separate row, grouped by party"""
        client = await self.db_client.get_client()

        # Get orders with party and quality details (same as partywise detail)
        orders_query = (
            client.table("orders")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("is_active", True)
        )

        orders_result = orders_query.order("order_date", desc=True).execute()

        if not orders_result.data:
            return []

        # Get order items for all orders
        order_ids = [order["id"] for order in orders_result.data]
        items_result = (
            client.table("order_items")
            .select("*")
            .in_("order_id", order_ids)
            .eq("is_active", True)
            .execute()
        )

        # Group items by order
        items_by_order = {}
        for item in items_result.data:
            order_id = item["order_id"]
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append(item)

        # Get existing lot data for these orders (if any lots exist)
        existing_lots_result = (
            client.table("lot_register")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("is_active", True)
            .execute()
        )

        # Get lot allocations
        lot_allocations_result = (
            client.table("lot_allocations").select("*").eq("is_active", True).execute()
        )

        # Create a map of order_id -> lot data for quick lookup
        order_to_lot_map = {}
        for allocation in lot_allocations_result.data:
            order_id = allocation["order_id"]
            if order_id not in order_to_lot_map:
                order_to_lot_map[order_id] = []
            order_to_lot_map[order_id].append(allocation)

        # Build lot register data - each design gets its own row
        lot_register_data = []
        for order in orders_result.data:
            order_id = order["id"]
            order_items = items_by_order.get(order_id, [])
            existing_allocations = order_to_lot_map.get(order_id, [])

            # Get all unique design numbers for this order
            all_design_numbers = set()
            for item in order_items:
                if item["design_number"]:
                    if item["design_number"] == "ALL":
                        # For "ALL", generate design numbers based on total_designs
                        design_numbers = [
                            f"D{i + 1:03d}"
                            for i in range(order.get("total_designs", 1))
                        ]
                    else:
                        # Split comma-separated design numbers
                        design_numbers = [
                            d.strip()
                            for d in item["design_number"].split(",")
                            if d.strip()
                        ]
                    all_design_numbers.update(design_numbers)

            # Create a row for each unique design number
            for design_no in sorted(all_design_numbers):
                # Find lot data specifically for this design
                lot_data = None
                allocation_id = None

                for allocation in existing_allocations:
                    if allocation["design_number"] == design_no:
                        # Find the lot for this specific design allocation
                        for lot in existing_lots_result.data:
                            if lot["id"] == allocation["lot_id"]:
                                lot_data = lot
                                allocation_id = allocation["id"]
                                break
                        break

                # Get ground color names for this design (comma-separated)
                ground_colors = []
                for item in order_items:
                    item_designs = []
                    if item["design_number"] == "ALL":
                        item_designs = [
                            f"D{i + 1:03d}"
                            for i in range(order.get("total_designs", 1))
                        ]
                    else:
                        item_designs = [
                            d.strip()
                            for d in item["design_number"].split(",")
                            if d.strip()
                        ]

                    if design_no in item_designs:
                        ground_colors.append(item["ground_color_name"])

                ground_color_str = ", ".join(ground_colors)

                lot_register_data.append(
                    {
                        "lot_date": lot_data["lot_date"] if lot_data else None,
                        "lot_no": lot_data["lot_number"] if lot_data else None,
                        "party_name": order["parties"]["party_name"],
                        "design_no": design_no,
                        "quality": order["qualities"]["quality_name"],
                        "total_pieces": order["units"],  # Total units for this design
                        "bill_no": lot_data["bill_number"] if lot_data else None,
                        "actual_pieces": lot_data["actual_pieces"]
                        if lot_data
                        else None,
                        "delivery_date": lot_data["delivery_date"]
                        if lot_data
                        else None,
                        "status": lot_data["status"] if lot_data else "PENDING",
                        "lot_id": lot_data["id"] if lot_data else None,
                        "allocation_id": allocation_id,
                        "ground_color_name": ground_color_str,
                        "order_id": order_id,
                        "order_item_id": None,  # Not applicable for combined rows
                        "party_id": order["party_id"],
                        "quality_id": order["quality_id"],
                    }
                )
        return lot_register_data

    async def update_lot_field(self, lot_id: int, field: str, value: str) -> bool:
        """Update a specific field of a lot (for inline editing)"""
        client = await self.db_client.get_client()

        # Validate field name
        allowed_fields = [
            "bill_number",
            "actual_pieces",
            "delivery_date",
            "lot_date",
            "lot_number",
        ]
        if field not in allowed_fields:
            raise ValueError(f"Field '{field}' is not allowed for update")

        # Prepare update data
        update_data = {
            field: value if field != "actual_pieces" else int(value) if value else None,
            "updated_at": get_ist_timestamp(),
        }

        # Update lot
        result = (
            client.table("lot_register").update(update_data).eq("id", lot_id).execute()
        )

        return bool(result.data)

    async def create_lot_for_design(
        self,
        order_id: int,
        design_number: str,
        lot_number: str,
        lot_date: str,
        party_id: int,
        quality_id: int,
        bill_number: str = None,
        actual_pieces: int = None,
        delivery_date: str = None,
    ) -> dict:
        """Create a lot for a specific design when lot number is entered in the register"""
        client = await self.db_client.get_client()

        # Get order details
        order_result = (
            client.table("orders")
            .select("units, total_designs")
            .eq("id", order_id)
            .execute()
        )

        if not order_result.data:
            raise ValueError(f"Order {order_id} not found")

        order = order_result.data[0]

        # Get order items for this specific design
        items_result = (
            client.table("order_items")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        if not items_result.data:
            raise ValueError(f"No order items found for order {order_id}")

        # Calculate total pieces for this design
        # Formula: units * 1 (since we're creating one lot per design)
        total_pieces = order["units"]

        # Create lot for this specific design
        lot_insert_data = {
            "party_id": party_id,
            "quality_id": quality_id,
            "lot_date": lot_date,
            "lot_number": lot_number,
            "total_pieces": total_pieces,
            "bill_number": bill_number,
            "actual_pieces": actual_pieces,
            "delivery_date": delivery_date,
            "status": "PENDING",
            "created_at": get_ist_timestamp(),
            "updated_at": get_ist_timestamp(),
        }

        lot_result = client.table("lot_register").insert(lot_insert_data).execute()
        lot = lot_result.data[0]

        # Create allocations for this specific design across all ground colors
        for item in items_result.data:
            # Check if this item contains the design we're creating a lot for
            item_designs = []
            if item["design_number"]:
                if item["design_number"] == "ALL":
                    # For "ALL", generate design numbers based on total_designs
                    item_designs = [
                        f"D{i + 1:03d}" for i in range(order.get("total_designs", 1))
                    ]
                else:
                    # Split comma-separated design numbers
                    item_designs = [
                        d.strip() for d in item["design_number"].split(",") if d.strip()
                    ]

            # If this item contains our target design, create allocation
            if design_number in item_designs:
                allocation_data = {
                    "lot_id": lot["id"],
                    "order_id": order_id,
                    "design_number": design_number,
                    "ground_color_name": item["ground_color_name"],
                    "beam_color_id": item["beam_color_id"],
                    "allocated_pieces": 1,  # Each ground color gets 1 piece
                    "created_at": get_ist_timestamp(),
                    "updated_at": get_ist_timestamp(),
                }
                client.table("lot_allocations").insert(allocation_data).execute()

        return lot

    async def create_lot_from_register(
        self,
        order_id: int,
        lot_number: str,
        lot_date: str,
        party_id: int,
        quality_id: int,
    ) -> dict:
        """Create a lot when lot number is entered in the register (legacy method)"""
        # This method creates a lot for the entire order (all designs)
        # For individual design lots, use create_lot_for_design instead
        client = await self.db_client.get_client()

        # Get order details
        order_result = (
            client.table("orders")
            .select("units, total_designs")
            .eq("id", order_id)
            .execute()
        )

        if not order_result.data:
            raise ValueError(f"Order {order_id} not found")

        order = order_result.data[0]

        # Get order items for this order
        items_result = (
            client.table("order_items")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        if not items_result.data:
            raise ValueError(f"No order items found for order {order_id}")

        # Calculate total pieces for the entire order
        total_pieces = order["units"] * order["total_designs"]

        # Create lot for the entire order
        lot_insert_data = {
            "party_id": party_id,
            "quality_id": quality_id,
            "lot_date": lot_date,
            "lot_number": lot_number,
            "total_pieces": total_pieces,
            "status": "PENDING",
            "created_at": get_ist_timestamp(),
            "updated_at": get_ist_timestamp(),
        }

        lot_result = client.table("lot_register").insert(lot_insert_data).execute()
        lot = lot_result.data[0]

        # Create allocations for all designs and ground colors
        for item in items_result.data:
            # Split design numbers
            design_numbers = []
            if item["design_number"]:
                if item["design_number"] == "ALL":
                    # For "ALL", generate design numbers based on total_designs
                    design_numbers = [
                        f"D{i + 1:03d}" for i in range(order.get("total_designs", 1))
                    ]
                else:
                    # Split comma-separated design numbers
                    design_numbers = [
                        d.strip() for d in item["design_number"].split(",") if d.strip()
                    ]

            # Create allocation for each design number
            for design_no in design_numbers:
                allocation_data = {
                    "lot_id": lot["id"],
                    "order_id": order_id,
                    "design_number": design_no,
                    "ground_color_name": item["ground_color_name"],
                    "beam_color_id": item["beam_color_id"],
                    "allocated_pieces": 1,  # Each ground color gets 1 piece
                    "created_at": get_ist_timestamp(),
                    "updated_at": get_ist_timestamp(),
                }
                client.table("lot_allocations").insert(allocation_data).execute()

        return lot

    async def get_order_item_status(self, order_id: Optional[int] = None) -> List[dict]:
        """Get order item status (allocated vs remaining)"""
        client = await self.db_client.get_client()

        query = (
            client.table("order_item_status")
            .select("""
                *,
                orders!inner(order_number, rate_per_piece),
                parties!inner(party_name),
                qualities!inner(quality_name),
                colors!inner(color_code, color_name)
            """)
            .eq("is_active", True)
        )

        if order_id:
            query = query.eq("order_id", order_id)

        result = query.execute()

        # Process results
        processed_results = []
        for item in result.data:
            processed_item = {
                **item,
                "order_number": item["orders"]["order_number"],
                "rate_per_piece": item["orders"]["rate_per_piece"],
                "party_name": item["parties"]["party_name"],
                "quality_name": item["qualities"]["quality_name"],
                "beam_color_code": item["colors"]["color_code"],
                "beam_color_name": item["colors"]["color_name"],
            }
            # Remove nested data
            del processed_item["orders"]
            del processed_item["parties"]
            del processed_item["qualities"]
            del processed_item["colors"]
            processed_results.append(processed_item)

        return processed_results

    async def get_beam_summary_with_allocation(self) -> List[dict]:
        """Get beam summary with allocation details"""
        client = await self.db_client.get_client()

        # Use the view for beam summary with allocation
        result = (
            client.table("beam_summary_with_allocation")
            .select("*")
            .order("quality_name", "party_name")
            .execute()
        )

        # Calculate allocation percentage
        processed_results = []
        for item in result.data:
            allocation_percentage = 0
            if item["total_pieces"] > 0:
                allocation_percentage = (
                    item["allocated_pieces"] / item["total_pieces"]
                ) * 100

            processed_item = {
                **item,
                "allocation_percentage": round(allocation_percentage, 2),
            }
            processed_results.append(processed_item)

        return processed_results

    async def get_allocation_summary(self) -> dict:
        """Get overall allocation summary statistics"""
        client = await self.db_client.get_client()

        # Get order statistics
        orders_result = (
            client.table("orders")
            .select("id, total_pieces")
            .eq("is_active", True)
            .execute()
        )

        # Get allocation statistics
        status_result = (
            client.table("order_item_status")
            .select("total_pieces, allocated_pieces, remaining_pieces")
            .eq("is_active", True)
            .execute()
        )

        # Get lot statistics
        lots_result = (
            client.table("lot_register")
            .select("id, status")
            .eq("is_active", True)
            .execute()
        )

        # Calculate totals
        total_orders = len(orders_result.data)
        total_pieces = sum(item["total_pieces"] for item in status_result.data)
        allocated_pieces = sum(item["allocated_pieces"] for item in status_result.data)
        remaining_pieces = sum(item["remaining_pieces"] for item in status_result.data)

        allocation_percentage = 0
        if total_pieces > 0:
            allocation_percentage = (allocated_pieces / total_pieces) * 100

        total_lots = len(lots_result.data)
        pending_lots = len(
            [lot for lot in lots_result.data if lot["status"] == "PENDING"]
        )
        completed_lots = len(
            [
                lot
                for lot in lots_result.data
                if lot["status"] in ["COMPLETED", "DELIVERED"]
            ]
        )

        return {
            "total_orders": total_orders,
            "total_pieces": total_pieces,
            "allocated_pieces": allocated_pieces,
            "remaining_pieces": remaining_pieces,
            "allocation_percentage": round(allocation_percentage, 2),
            "total_lots": total_lots,
            "pending_lots": pending_lots,
            "completed_lots": completed_lots,
        }

    async def initialize_order_item_status(self, order_id: int) -> None:
        """Initialize order item status after order creation"""
        client = await self.db_client.get_client()

        # Get order items
        items_result = (
            client.table("order_items")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        # Get order details for calculation
        order_result = (
            client.table("orders")
            .select("units, total_designs")
            .eq("id", order_id)
            .execute()
        )

        if not order_result.data:
            return

        order = order_result.data[0]

        # Create status entries for each unique design/color combination
        for item in items_result.data:
            # Calculate total pieces for this design/color combination
            # Formula: units * total_designs * 1 (since each ground color maps to one beam color)
            total_pieces = order["units"] * order["total_designs"]

            status_data = {
                "order_id": order_id,
                "design_number": item["design_number"],
                "ground_color_name": item["ground_color_name"],
                "beam_color_id": item["beam_color_id"],
                "total_pieces": total_pieces,
                "allocated_pieces": 0,
                "remaining_pieces": total_pieces,
                "created_at": get_ist_timestamp(),
                "updated_at": get_ist_timestamp(),
            }

            # Insert or update status
            client.table("order_item_status").insert(status_data).execute()

    async def count_lots(self) -> int:
        """Count total active lots"""
        client = await self.db_client.get_client()

        result = (
            client.table("lot_register")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return result.count or 0
