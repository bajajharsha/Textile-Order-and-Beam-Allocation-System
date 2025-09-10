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

        # Generate order number
        order_number = await self._generate_order_number(client)

        # Prepare order data
        main_order_data = {
            "order_number": order_number,
            "party_id": order_data["party_id"],
            "quality_id": order_data["quality_id"],
            "order_date": str(date.today()),
            "rate_per_piece": float(order_data["rate_per_piece"]),
            "total_designs": len(order_data["design_numbers"]),
            "notes": order_data.get("notes"),
            "created_at": get_ist_timestamp(),
            "updated_at": get_ist_timestamp(),
        }

        # Create main order
        order_result = client.table("orders").insert(main_order_data).execute()
        order = Order.from_dict(order_result.data[0])

        # Create order cuts
        for cut_value in order_data["cuts"]:
            cut_data = {
                "order_id": order.id,
                "cut_value": cut_value,
                "created_at": get_ist_timestamp(),
            }
            client.table("order_cuts").insert(cut_data).execute()

        # Create order items and calculate beam summary
        ground_colors = order_data["ground_colors"]

        for i, design_number in enumerate(order_data["design_numbers"]):
            # For each design, create items for each ground color
            for ground_color in ground_colors:
                item_data = {
                    "order_id": order.id,
                    "design_number": design_number,
                    "ground_color_id": ground_color["ground_color_id"],
                    "beam_color_id": ground_color["beam_color_id"],
                    "pieces_per_color": ground_color["pieces_per_color"],
                    "created_at": get_ist_timestamp(),
                }
                client.table("order_items").insert(item_data).execute()

        # Calculate totals and update order
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

    async def update(self, order_id: int, update_data: dict) -> Optional[Order]:
        """Update order"""
        client = await self.db_client.get_client()

        # Update main order
        main_update_data = {}
        for key in ["party_id", "quality_id", "rate_per_piece", "notes"]:
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

            # Create new items
            pieces_per_color = update_data.get("pieces_per_color", 0)
            for design_number in update_data["design_numbers"]:
                for ground_color in update_data["ground_colors"]:
                    item_data = {
                        "order_id": order_id,
                        "design_number": design_number,
                        "ground_color_id": ground_color["ground_color_id"],
                        "beam_color_id": ground_color["beam_color_id"],
                        "pieces_per_color": pieces_per_color,
                        "created_at": get_ist_timestamp(),
                    }
                    client.table("order_items").insert(item_data).execute()

            # Recalculate totals
            beam_summary = await self._calculate_beam_summary(order_id, client)
            total_designs = len(update_data["design_numbers"])
            total_pieces = sum(beam_summary.values()) * pieces_per_color * total_designs

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
        """Calculate total pieces for an order from all order items"""
        # Get all items for the order with their pieces_per_color
        items_result = (
            client.table("order_items")
            .select("pieces_per_color")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .execute()
        )

        # Sum up all pieces
        total_pieces = sum(item["pieces_per_color"] for item in items_result.data)
        return total_pieces
