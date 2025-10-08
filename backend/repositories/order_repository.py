"""
Order Repository - Database operations with calculations
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from config.database import database, get_ist_timestamp
from models.domain.order import Order, OrderItem


class OrderRepository:
    """Order database operations"""

    def __init__(self):
        self.db_client = database

    async def create(self, order_data: dict) -> Order:
        """Create new order with cuts and items"""
        client = await self.db_client.get_client()

        # Generate order number - format is ORD-2025-08-01-001
        order_number = await self._generate_order_number(client)

        # Prepare order data
        main_order_data = {
            "order_number": order_number,
            "party_id": order_data["party_id"],
            "quality_id": order_data["quality_id"],
            "sets": order_data["sets"],
            "pick": order_data["pick"],
            "lot_register_type": order_data["lot_register_type"],
            "order_date": str(date.today()),
            "rate_per_piece": float(order_data["rate_per_piece"]),
            "total_designs": len(order_data["design_numbers"]),
            "notes": order_data.get("notes"),
            "created_at": get_ist_timestamp(),
            "updated_at": get_ist_timestamp(),
        }

        # Create main order in table "orders"
        order_result = client.table("orders").insert(main_order_data).execute()
        order = Order.from_dict(order_result.data[0])

        print("Order created in 'orders' table")

        # Create order cuts in table "order_cuts"
        for cut_value in order_data["cuts"]:
            cut_data = {
                "order_id": order.id,
                "cut_value": cut_value,
                "created_at": get_ist_timestamp(),
            }
            client.table("order_cuts").insert(cut_data).execute()

        # Create order items for ground colors with design numbers
        ground_colors = order_data["ground_colors"]
        design_numbers = order_data["design_numbers"]

        # Create items for each ground color (not per design to avoid duplication)
        for ground_color in ground_colors:
            item_data = {
                "order_id": order.id,
                "design_number": ",".join(
                    design_numbers
                ),  # Store all design numbers as comma-separated
                "ground_color_name": ground_color["ground_color_name"],
                "beam_color_id": ground_color["beam_color_id"],
                "created_at": get_ist_timestamp(),
            }
            client.table("order_items").insert(item_data).execute()
        # Calculate totals and update order in table "orders"
        beam_summary = await self._calculate_beam_summary(order.id, client)
        total_pieces = await self._calculate_total_pieces(order.id, client)
        total_value = float(
            Decimal(str(total_pieces)) * Decimal(str(order.rate_per_piece))
        )

        # Update order with calculated values
        client.table("orders").update(
            {
                "total_pieces": total_pieces,
                "total_value": total_value,
                "updated_at": get_ist_timestamp(),
            }
        ).eq("id", order.id).execute()

        # Initialize order item status for lot allocation
        await self._initialize_order_item_status(order.id, client)

        # NEW: Initialize design tracking for set-based allocation
        await self._initialize_design_tracking(order.id, order_data, client)

        # Return updated order
        return await self.get_by_id(order.id)

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with all related data"""
        client = await self.db_client.get_client()

        # Get main order
        order_result = (
            client.table("orders")
            .select("*")
            .eq("id", order_id)
            .eq("is_active", True)
            .execute()
        )

        if not order_result.data:
            return None

        order = Order.from_dict(order_result.data[0])
        return order

    async def get_all_orders(self) -> List[Order]:
        """Get all active orders with party and quality details"""
        client = await self.db_client.get_client()

        # Get orders with party and quality information
        orders_result = (
            client.table("orders")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .eq("is_active", True)
            .order("created_at", desc=True)
            .execute()
        )

        orders = []
        for order_data in orders_result.data:
            # Create order object and add party/quality names
            order = Order.from_dict(order_data)
            order.party_name = order_data["parties"]["party_name"]
            order.quality_name = order_data["qualities"]["quality_name"]
            orders.append(order)

        return orders

    async def get_all_orders_with_details(
        self, filters: dict = None, limit: int = None, offset: int = None
    ) -> List[dict]:
        """Get all active orders with all related data for API responses - OPTIMIZED"""
        client = await self.db_client.get_client()

        # Build query with filters
        query = (
            client.table("orders")
            .select("""
            *,
            parties!inner(id, party_name),
            qualities!inner(id, quality_name)
        """)
            .eq("is_active", True)
        )

        # Apply filters
        if filters:
            if "party_id" in filters:
                query = query.eq("party_id", filters["party_id"])
            if "quality_id" in filters:
                query = query.eq("quality_id", filters["quality_id"])

        # Apply pagination
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.range(offset, offset + (limit or 10) - 1)

        # Execute main query
        orders_result = query.order("created_at", desc=True).execute()

        if not orders_result.data:
            return []

        order_ids = [order["id"] for order in orders_result.data]

        # Batch fetch all related data
        # 1. Get all cuts for all orders
        cuts_result = (
            client.table("order_cuts")
            .select("order_id, cut_value")
            .in_("order_id", order_ids)
            .eq("is_active", True)
            .execute()
        )
        cuts_by_order = {}
        for cut in cuts_result.data:
            order_id = cut["order_id"]
            if order_id not in cuts_by_order:
                cuts_by_order[order_id] = []
            cuts_by_order[order_id].append(cut["cut_value"])

        # 2. Get all order items for all orders
        items_result = (
            client.table("order_items")
            .select("*")
            .in_("order_id", order_ids)
            .eq("is_active", True)
            .execute()
        )
        items_by_order = {}
        beam_color_ids = set()
        for item in items_result.data:
            order_id = item["order_id"]
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append(item)
            beam_color_ids.add(item["beam_color_id"])

        # 3. Get all color codes in one query
        color_codes = {}
        if beam_color_ids:
            colors_result = (
                client.table("colors")
                .select("id, color_code")
                .in_("id", list(beam_color_ids))
                .execute()
            )
            color_codes = {
                color["id"]: color["color_code"] for color in colors_result.data
            }

        # 4. Process each order
        orders_with_details = []
        for order_data in orders_result.data:
            order_id = order_data["id"]

            # Get cuts for this order
            cuts = cuts_by_order.get(order_id, [])

            # Get items for this order
            items = items_by_order.get(order_id, [])

            # Process ground colors and beam color counts
            ground_colors = []
            beam_color_counts = {}
            design_numbers = []

            for item in items:
                ground_colors.append(
                    {
                        "ground_color_name": item["ground_color_name"],
                        "beam_color_id": item["beam_color_id"],
                    }
                )

                # Count beam colors
                beam_color_id = item["beam_color_id"]
                beam_color_counts[beam_color_id] = (
                    beam_color_counts.get(beam_color_id, 0) + 1
                )

                # Process design numbers
                if item["design_number"]:
                    if item["design_number"] == "ALL":
                        # For old orders with "ALL", generate design numbers based on total_designs
                        design_numbers.extend(
                            [
                                f"D{i + 1:03d}"
                                for i in range(order_data["total_designs"])
                            ]
                        )
                    else:
                        # Split comma-separated design numbers
                        design_numbers.extend(
                            [
                                d.strip()
                                for d in item["design_number"].split(",")
                                if d.strip()
                            ]
                        )

            design_numbers = list(set(design_numbers))  # Remove duplicates

            # Create beam_summary with color codes
            beam_summary = {}
            for beam_color_id, count in beam_color_counts.items():
                color_code = color_codes.get(beam_color_id)
                if color_code:
                    beam_summary[color_code] = count

            # Create order items for calculation
            order_items = []
            for item in items:
                beam_color_id = item["beam_color_id"]
                count = beam_color_counts[beam_color_id]
                calculated_pieces = (
                    order_data["sets"] * order_data["total_designs"] * count
                )

                order_items.append(
                    {
                        "design_number": item["design_number"],
                        "ground_color_name": item["ground_color_name"],
                        "beam_color_id": beam_color_id,
                        "calculated_pieces": calculated_pieces,
                    }
                )

            # Build complete order data
            order_with_details = {
                **order_data,
                "party_name": order_data["parties"]["party_name"],
                "quality_name": order_data["qualities"]["quality_name"],
                "cuts": cuts,
                "design_numbers": design_numbers,
                "ground_colors": ground_colors,
                "beam_summary": beam_summary,
                "order_items": order_items,
            }

            # Remove nested data
            del order_with_details["parties"]
            del order_with_details["qualities"]

            orders_with_details.append(order_with_details)

        return orders_with_details

    async def search_with_details(self, query: str, limit: int = 20) -> List[dict]:
        """Search orders with all related data"""
        client = await self.db_client.get_client()

        # Search in orders table
        order_result = (
            client.table("orders")
            .select("""
                *,
                parties!inner(id, party_name),
                qualities!inner(id, quality_name)
            """)
            .ilike("order_number", f"%{query}%")
            .eq("is_active", True)
            .limit(limit)
            .execute()
        )

        found_order_ids = set()
        orders_with_details = []

        # Process orders found by order number
        for order_data in order_result.data:
            found_order_ids.add(order_data["id"])
            order_with_details = await self._build_order_with_details(
                order_data, client
            )
            orders_with_details.append(order_with_details)

        # Also search in order items for design numbers if we haven't reached the limit
        if len(orders_with_details) < limit:
            item_result = (
                client.table("order_items")
                .select("order_id")
                .ilike("design_number", f"%{query}%")
                .eq("is_active", True)
                .limit(limit - len(orders_with_details))
                .execute()
            )

            # Get unique order IDs from items
            item_order_ids = list(set([item["order_id"] for item in item_result.data]))

            # Get full order data for these IDs
            for order_id in item_order_ids:
                if order_id not in found_order_ids and len(orders_with_details) < limit:
                    order_data_result = (
                        client.table("orders")
                        .select("""
                            *,
                            parties!inner(id, party_name),
                            qualities!inner(id, quality_name)
                        """)
                        .eq("id", order_id)
                        .eq("is_active", True)
                        .execute()
                    )

                    if order_data_result.data:
                        order_data = order_data_result.data[0]
                        order_with_details = await self._build_order_with_details(
                            order_data, client
                        )
                        orders_with_details.append(order_with_details)

        return orders_with_details

    async def _build_order_with_details(self, order_data: dict, client) -> dict:
        """Helper method to build order with all details"""
        order_id = order_data["id"]

        # Get order cuts
        cuts_result = (
            client.table("order_cuts")
            .select("cut_value")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )
        cuts = [cut["cut_value"] for cut in cuts_result.data]

        # Get order items (ground colors)
        items_result = (
            client.table("order_items")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )
        ground_colors = []
        beam_color_counts = {}

        for item in items_result.data:
            ground_colors.append(
                {
                    "ground_color_name": item["ground_color_name"],
                    "beam_color_id": item["beam_color_id"],
                }
            )

            # Count beam colors for beam_summary
            beam_color_id = item["beam_color_id"]
            beam_color_counts[beam_color_id] = (
                beam_color_counts.get(beam_color_id, 0) + 1
            )

        # Get actual design numbers from order items
        design_numbers_result = (
            client.table("order_items")
            .select("design_number")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )
        design_numbers = []
        for item in design_numbers_result.data:
            if item["design_number"]:
                if item["design_number"] == "ALL":
                    # For old orders with "ALL", generate design numbers based on total_designs
                    design_numbers.extend(
                        [f"D{i + 1:03d}" for i in range(order_data["total_designs"])]
                    )
                else:
                    # Split comma-separated design numbers and add to list
                    design_numbers.extend(
                        [
                            d.strip()
                            for d in item["design_number"].split(",")
                            if d.strip()
                        ]
                    )
        design_numbers = list(set(design_numbers))  # Remove duplicates

        # Create beam_summary with color codes
        beam_summary = {}
        for beam_color_id, count in beam_color_counts.items():
            # Get color code
            color_result = (
                client.table("colors")
                .select("color_code")
                .eq("id", beam_color_id)
                .execute()
            )
            if color_result.data:
                color_code = color_result.data[0]["color_code"]
                beam_summary[color_code] = count

        # Create order items for calculation (with calculated_pieces)
        order_items = []
        for item in items_result.data:
            beam_color_id = item["beam_color_id"]
            count = beam_color_counts[beam_color_id]
            calculated_pieces = order_data["sets"] * order_data["total_designs"] * count

            order_items.append(
                {
                    "design_number": item["design_number"],
                    "ground_color_name": item["ground_color_name"],
                    "beam_color_id": beam_color_id,
                    "calculated_pieces": calculated_pieces,
                }
            )

        # Build complete order data
        order_with_details = {
            **order_data,
            "party_name": order_data["parties"]["party_name"],
            "quality_name": order_data["qualities"]["quality_name"],
            "cuts": cuts,
            "design_numbers": design_numbers,
            "ground_colors": ground_colors,
            "beam_summary": beam_summary,
            "order_items": order_items,
        }

        # Remove the nested party/quality data
        del order_with_details["parties"]
        del order_with_details["qualities"]

        return order_with_details

    async def update(self, order_id: int, update_data: dict) -> Optional[Order]:
        """Update order"""
        client = await self.db_client.get_client()

        # Update main order
        main_update_data = {}
        for key in [
            "party_id",
            "quality_id",
            "sets",
            "pick",
            "lot_register_type",
            "rate_per_piece",
            "notes",
        ]:
            if key in update_data:
                if key == "rate_per_piece":
                    main_update_data[key] = float(update_data[key])
                else:
                    main_update_data[key] = update_data[key]

        if main_update_data:
            main_update_data["updated_at"] = get_ist_timestamp()
            client.table("orders").update(main_update_data).eq("id", order_id).execute()

        # Update cuts if provided
        if "cuts" in update_data:
            # Delete existing cuts
            client.table("order_cuts").update({"is_active": False}).eq(
                "order_id", order_id
            ).execute()

            # Create new cuts
            for cut_value in update_data["cuts"]:
                cut_data = {
                    "order_id": order_id,
                    "cut_value": cut_value,
                    "created_at": get_ist_timestamp(),
                }
                client.table("order_cuts").insert(cut_data).execute()

        # Update order items if provided
        if "design_numbers" in update_data and "ground_colors" in update_data:
            # Delete existing items
            client.table("order_items").update({"is_active": False}).eq(
                "order_id", order_id
            ).execute()

            # Create new items for ground colors with design numbers
            for ground_color in update_data["ground_colors"]:
                item_data = {
                    "order_id": order_id,
                    "design_number": ",".join(
                        update_data["design_numbers"]
                    ),  # Store all design numbers as comma-separated
                    "ground_color_name": ground_color["ground_color_name"],
                    "beam_color_id": ground_color["beam_color_id"],
                    "created_at": get_ist_timestamp(),
                }
                client.table("order_items").insert(item_data).execute()

            # Recalculate totals
            beam_summary = await self._calculate_beam_summary(order_id, client)
            total_designs = len(update_data["design_numbers"])
            total_pieces = await self._calculate_total_pieces(order_id, client)

            # Get current rate
            current_order = await self.get_by_id(order_id)
            rate_per_piece = update_data.get(
                "rate_per_piece", current_order.rate_per_piece
            )
            total_value = float(
                Decimal(str(total_pieces)) * Decimal(str(rate_per_piece))
            )

            # Update calculated values
            client.table("orders").update(
                {
                    "total_designs": total_designs,
                    "total_pieces": total_pieces,
                    "total_value": total_value,
                    "updated_at": get_ist_timestamp(),
                }
            ).eq("id", order_id).execute()

        return await self.get_by_id(order_id)

    async def delete(self, order_id: int) -> bool:
        """Soft delete order and related data"""
        client = await self.db_client.get_client()

        # Soft delete order
        order_result = (
            client.table("orders")
            .update({"is_active": False, "updated_at": get_ist_timestamp()})
            .eq("id", order_id)
            .execute()
        )

        # Soft delete related data
        client.table("order_cuts").update({"is_active": False}).eq(
            "order_id", order_id
        ).execute()
        client.table("order_items").update({"is_active": False}).eq(
            "order_id", order_id
        ).execute()

        return bool(order_result.data)

    async def get_all(self, limit: int = 20, offset: int = 0) -> List[Order]:
        """Get all active orders with pagination"""
        client = await self.db_client.get_client()
        result = (
            client.table("orders")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [Order.from_dict(order) for order in result.data]

    async def count_all(self) -> int:
        """Get total count of active orders"""
        client = await self.db_client.get_client()
        result = (
            client.table("orders")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return result.count or 0

    async def _initialize_order_item_status(self, order_id: int, client) -> None:
        """Initialize order item status for lot allocation tracking"""

        # Get order details
        order_result = (
            client.table("orders")
            .select("sets, total_designs")
            .eq("id", order_id)
            .execute()
        )

        if not order_result.data:
            return

        order = order_result.data[0]

        # Get order items
        items_result = (
            client.table("order_items")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        # Create status entries for each unique design/color combination
        for item in items_result.data:
            # Calculate total pieces for this item
            # Since we store comma-separated design numbers, we need to split and count
            design_numbers = []
            if item["design_number"] and item["design_number"] != "ALL":
                design_numbers = [
                    d.strip() for d in item["design_number"].split(",") if d.strip()
                ]
            else:
                # For old orders with "ALL", use total_designs
                design_numbers = [
                    f"D{i + 1:03d}" for i in range(order["total_designs"])
                ]

            # For each design number, create a status entry
            for design_number in design_numbers:
                # Calculate total pieces for this specific design/color combination
                total_pieces = order["sets"]  # Sets per design per color

                status_data = {
                    "order_id": order_id,
                    "design_number": design_number,
                    "ground_color_name": item["ground_color_name"],
                    "beam_color_id": item["beam_color_id"],
                    "total_pieces": total_pieces,
                    "allocated_pieces": 0,
                    "remaining_pieces": total_pieces,
                    "created_at": get_ist_timestamp(),
                    "updated_at": get_ist_timestamp(),
                }

                # Check if status already exists (avoid duplicates)
                existing_result = (
                    client.table("order_item_status")
                    .select("id")
                    .eq("order_id", order_id)
                    .eq("design_number", design_number)
                    .eq("ground_color_name", item["ground_color_name"])
                    .eq("is_active", True)
                    .execute()
                )

                if not existing_result.data:
                    client.table("order_item_status").insert(status_data).execute()

    async def search(self, query: str, limit: int = 20) -> List[Order]:
        """Search orders by order number or design numbers"""
        client = await self.db_client.get_client()

        # Search in orders table
        order_result = (
            client.table("orders")
            .select("*")
            .ilike("order_number", f"%{query}%")
            .eq("is_active", True)
            .limit(limit)
            .execute()
        )

        orders = [Order.from_dict(order) for order in order_result.data]

        # Also search in order items for design numbers
        if len(orders) < limit:
            item_result = (
                client.table("order_items")
                .select("order_id")
                .ilike("design_number", f"%{query}%")
                .eq("is_active", True)
                .limit(limit - len(orders))
                .execute()
            )

            order_ids = [item["order_id"] for item in item_result.data]
            if order_ids:
                additional_orders = (
                    client.table("orders")
                    .select("*")
                    .in_("id", order_ids)
                    .eq("is_active", True)
                    .execute()
                )
                orders.extend(
                    [Order.from_dict(order) for order in additional_orders.data]
                )

        return orders

    async def get_order_cuts(self, order_id: int) -> List[str]:
        """Get cuts for an order"""
        client = await self.db_client.get_client()
        result = (
            client.table("order_cuts")
            .select("cut_value")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )
        return [cut["cut_value"] for cut in result.data]

    async def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Get items for an order"""
        client = await self.db_client.get_client()
        result = (
            client.table("order_items")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )
        return [OrderItem.from_dict(item) for item in result.data]

    async def get_design_numbers(self, order_id: int) -> List[str]:
        """Get unique design numbers for an order"""
        client = await self.db_client.get_client()
        result = (
            client.table("order_items")
            .select("design_number")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )
        return list(set([item["design_number"] for item in result.data]))

    async def _generate_order_number(self, client) -> str:
        """Generate unique order number"""
        today = datetime.now()
        prefix = f"ORD-{today.year}-{today.month:02d}"

        # Get count of orders for this month
        result = (
            client.table("orders")
            .select("id", count="exact")
            .ilike("order_number", f"{prefix}%")
            .execute()
        )

        sequence = (result.count or 0) + 1
        return f"{prefix}-{sequence:03d}"

    async def _calculate_beam_summary(self, order_id: int, client) -> Dict[str, int]:
        """Calculate beam color summary for an order"""
        # Get all items for the order
        items_result = (
            client.table("order_items")
            .select("beam_color_id")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        # Count occurrences of each beam color
        beam_counts = {}
        for item in items_result.data:
            beam_color_id = item["beam_color_id"]
            beam_counts[beam_color_id] = beam_counts.get(beam_color_id, 0) + 1

        # Convert to color codes
        color_summary = {}
        for color_id, count in beam_counts.items():
            # Get color code
            color_result = (
                client.table("colors").select("color_code").eq("id", color_id).execute()
            )
            if color_result.data:
                color_code = color_result.data[0]["color_code"]
                color_summary[color_code] = count

        return color_summary

    async def _calculate_total_pieces(self, order_id: int, client) -> int:
        """Calculate total pieces using new formula: Sets × Total Designs × Beam Color Count"""
        # Get order details
        order_result = (
            client.table("orders")
            .select("sets, total_designs")
            .eq("id", order_id)
            .execute()
        )

        if not order_result.data:
            return 0

        order_data = order_result.data[0]
        sets = order_data["sets"]
        total_designs = order_data["total_designs"]

        # Get beam color counts
        items_result = (
            client.table("order_items")
            .select("beam_color_id")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        # Count beam color occurrences
        beam_color_counts = {}
        for item in items_result.data:
            beam_color_id = item["beam_color_id"]
            beam_color_counts[beam_color_id] = (
                beam_color_counts.get(beam_color_id, 0) + 1
            )

        # Calculate total pieces: Sets × Total Designs × Sum of all beam color counts
        total_beam_color_count = sum(beam_color_counts.values())
        total_pieces = sets * total_designs * total_beam_color_count

        return total_pieces

    async def _initialize_design_tracking(
        self, order_id: int, order_data: dict, client
    ) -> None:
        """Initialize design tracking tables for set-based allocation"""
        try:
            print(f"🔧 Initializing design tracking for order {order_id}...")

            sets = order_data["sets"]
            design_numbers = order_data["design_numbers"]
            ground_colors = order_data["ground_colors"]

            # Build a map of design_number -> {beam_color_id: count}
            design_beam_map = {}

            # Each ground color applies to ALL designs
            for ground_color in ground_colors:
                beam_id = ground_color["beam_color_id"]

                for design in design_numbers:
                    if design not in design_beam_map:
                        design_beam_map[design] = {}

                    # Count beam color occurrences (this becomes beam_multiplier)
                    if beam_id in design_beam_map[design]:
                        design_beam_map[design][beam_id] += 1
                    else:
                        design_beam_map[design][beam_id] = 1

            # Create design tracking and beam config for each design
            for design_number in design_numbers:
                # Create design_set_tracking entry
                tracking_data = {
                    "order_id": order_id,
                    "design_number": design_number,
                    "total_sets": sets,
                    "allocated_sets": 0,
                    "remaining_sets": sets,
                    "is_active": True,
                    "created_at": get_ist_timestamp(),
                    "updated_at": get_ist_timestamp(),
                }
                client.table("design_set_tracking").insert(tracking_data).execute()

                # Create design_beam_config entries
                if design_number in design_beam_map:
                    for beam_color_id, multiplier in design_beam_map[
                        design_number
                    ].items():
                        beam_config_data = {
                            "order_id": order_id,
                            "design_number": design_number,
                            "beam_color_id": beam_color_id,
                            "beam_multiplier": multiplier,
                            "is_active": True,
                            "created_at": get_ist_timestamp(),
                            # Note: design_beam_config table doesn't have updated_at column
                        }
                        client.table("design_beam_config").insert(
                            beam_config_data
                        ).execute()

            print(
                f"✅ Initialized design tracking: {len(design_numbers)} designs, {sets} sets each"
            )

        except Exception as e:
            print(f"❌ Failed to initialize design tracking: {str(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
            # Don't fail order creation if design tracking fails
            pass
