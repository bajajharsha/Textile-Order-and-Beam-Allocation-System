"""
Order repository for data access operations
Layer 3: Data Access Layer
"""

from typing import Dict, List, Optional

from config.logging import get_logger
from repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    """Repository for order data operations"""

    def __init__(self):
        super().__init__("orders")
        self.logger = get_logger("repositories.order")

    def _get_search_fields(self) -> List[str]:
        """Return list of fields that can be searched in order repository"""
        return ["order_number"]

    def _get_default_order_field(self) -> str:
        """Return default field for ordering order records"""
        return "order_date"

    async def get_by_order_number(self, order_number: str) -> Optional[Dict]:
        """Get order by order number"""
        try:
            self.logger.debug(f"Fetching order by number: {order_number}")

            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("order_number", order_number)
                .execute()
            )

            if not result.data:
                self.logger.debug(f"Order not found with number: {order_number}")
                return None

            return result.data[0]

        except Exception as e:
            self.logger.error(
                f"Error fetching order by number {order_number}: {str(e)}"
            )
            raise

    async def create_order_with_items(
        self, order_data: Dict, order_items: List[Dict], calc_service
    ) -> Dict:
        """Create order with its items in a transaction-like manner"""
        try:
            self.logger.info("Creating order with items")

            # Create the main order
            created_order = await self.create(order_data)
            order_id = created_order["id"]

            self.logger.info(f"Created order with ID: {order_id}")

            # Prepare order items with calculated pieces
            items_to_create = []
            total_designs = order_data.get("total_designs", 1)

            for item in order_items:
                # Calculate pieces using the calculation service
                calculated_pieces = calc_service.calculate_beam_pieces(
                    item.pieces_per_color, item.designs_per_beam, total_designs
                )

                item_data = {
                    "order_id": order_id,
                    "design_number": item.design_number,
                    "ground_color_id": item.ground_color_id,
                    "beam_color_id": item.beam_color_id,
                    "pieces_per_color": item.pieces_per_color,
                    "designs_per_beam": item.designs_per_beam,
                    "calculated_pieces": calculated_pieces,
                }

                items_to_create.append(item_data)

            # Create all order items
            if items_to_create:
                result = (
                    self.supabase.table("order_items").insert(items_to_create).execute()
                )

                if not result.data:
                    self.logger.error("Failed to create order items")
                    # In a real transaction, we would rollback the order creation
                    raise ValueError("Failed to create order items")

                created_items = result.data
                self.logger.info(f"Created {len(created_items)} order items")

                # Add items to the order response
                created_order["order_items"] = created_items

            return created_order

        except Exception as e:
            self.logger.error(f"Error creating order with items: {str(e)}")
            raise

    async def get_order_with_items(self, order_id: int) -> Optional[Dict]:
        """Get order with its items and related data"""
        try:
            self.logger.debug(f"Fetching order {order_id} with items")

            # Get order with joined data
            order_result = (
                self.supabase.table(self.table_name)
                .select(
                    """
                    *,
                    parties!inner(party_name),
                    qualities!inner(quality_name, feeder_count, specification)
                """
                )
                .eq("id", order_id)
                .execute()
            )

            if not order_result.data:
                self.logger.debug(f"Order {order_id} not found")
                return None

            order = order_result.data[0]

            # Get order items with color information
            items_result = (
                self.supabase.table("order_items")
                .select(
                    """
                    *,
                    ground_color:colors!ground_color_id(id, color_name, color_code),
                    beam_color:colors!beam_color_id(id, color_name, color_code)
                """
                )
                .eq("order_id", order_id)
                .order("design_number")
                .execute()
            )

            order_items = items_result.data or []
            order["order_items"] = order_items

            # Extract related data for easier access
            if order.get("parties"):
                order["party_name"] = order["parties"]["party_name"]

            if order.get("qualities"):
                quality_data = order["qualities"]
                order["quality_name"] = quality_data["quality_name"]
                order["feeder_count"] = quality_data["feeder_count"]
                order["specification"] = quality_data["specification"]

            self.logger.debug(
                f"Retrieved order {order_id} with {len(order_items)} items"
            )

            return order

        except Exception as e:
            self.logger.error(f"Error fetching order with items: {str(e)}")
            raise

    async def get_all_orders_with_details(
        self,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict]:
        """Get all orders with basic details"""
        try:
            self.logger.debug("Fetching all orders with details")

            query = (
                self.supabase.table(self.table_name)
                .select(
                    """
                    *,
                    parties!inner(party_name),
                    qualities!inner(quality_name)
                """
                )
                .order("order_date", desc=True)
            )

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)

            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            result = query.execute()
            orders = result.data or []

            # Get order items for each order to calculate totals
            for order in orders:
                order_id = order["id"]

                # Get order items
                items_result = (
                    self.supabase.table("order_items")
                    .select("calculated_pieces")
                    .eq("order_id", order_id)
                    .execute()
                )

                order_items = items_result.data or []
                order["order_items"] = order_items

                # Extract related data
                if order.get("parties"):
                    order["party_name"] = order["parties"]["party_name"]
                if order.get("qualities"):
                    order["quality_name"] = order["qualities"]["quality_name"]

            self.logger.debug(f"Retrieved {len(orders)} orders with details")

            return orders

        except Exception as e:
            self.logger.error(f"Error fetching orders with details: {str(e)}")
            raise

    async def get_orders_by_party(
        self, party_id: int, limit: Optional[int] = None
    ) -> List[Dict]:
        """Get orders for a specific party"""
        try:
            self.logger.debug(f"Fetching orders for party {party_id}")

            query = (
                self.supabase.table(self.table_name)
                .select(
                    """
                    *,
                    qualities!inner(quality_name)
                """
                )
                .eq("party_id", party_id)
                .order("order_date", desc=True)
            )

            if limit:
                query = query.limit(limit)

            result = query.execute()
            orders = result.data or []

            # Get order items for each order
            for order in orders:
                items_result = (
                    self.supabase.table("order_items")
                    .select("calculated_pieces, design_number")
                    .eq("order_id", order["id"])
                    .execute()
                )

                order["order_items"] = items_result.data or []

                # Extract quality name
                if order.get("qualities"):
                    order["quality_name"] = order["qualities"]["quality_name"]

            self.logger.debug(f"Found {len(orders)} orders for party {party_id}")

            return orders

        except Exception as e:
            self.logger.error(f"Error fetching orders for party {party_id}: {str(e)}")
            raise

    async def get_orders_for_quality_summary(self) -> List[Dict]:
        """Get orders data for quality-wise beam summary"""
        try:
            self.logger.debug("Fetching orders for quality summary")

            # Get all orders with quality and items
            result = (
                self.supabase.table(self.table_name)
                .select(
                    """
                    id,
                    order_number,
                    party_id,
                    order_date,
                    qualities!inner(quality_name)
                """
                )
                .order("order_date", desc=True)
                .execute()
            )

            orders = result.data or []

            # Get order items with color information for each order
            for order in orders:
                items_result = (
                    self.supabase.table("order_items")
                    .select(
                        """
                        design_number,
                        calculated_pieces,
                        beam_color:colors!beam_color_id(color_name, color_code)
                    """
                    )
                    .eq("order_id", order["id"])
                    .execute()
                )

                order_items = items_result.data or []

                # Add beam color name to items
                for item in order_items:
                    if item.get("beam_color"):
                        item["beam_color_name"] = item["beam_color"]["color_name"]
                        item["beam_color_code"] = item["beam_color"]["color_code"]
                    else:
                        item["beam_color_name"] = "Unknown"
                        item["beam_color_code"] = "UNK"

                order["order_items"] = order_items

                # Extract quality name
                if order.get("qualities"):
                    order["quality_name"] = order["qualities"]["quality_name"]

            self.logger.debug(
                f"Retrieved {len(orders)} orders for quality summary generation"
            )

            return orders

        except Exception as e:
            self.logger.error(f"Error fetching orders for quality summary: {str(e)}")
            raise

    async def search_orders(
        self,
        search_term: str,
        party_id: Optional[int] = None,
        quality_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Search orders by multiple criteria"""
        try:
            self.logger.debug(f"Searching orders with term: {search_term}")

            query = (
                self.supabase.table(self.table_name)
                .select(
                    """
                    *,
                    parties!inner(party_name),
                    qualities!inner(quality_name)
                """
                )
                .ilike("order_number", f"%{search_term}%")
            )

            # Apply additional filters
            if party_id:
                query = query.eq("party_id", party_id)
            if quality_id:
                query = query.eq("quality_id", quality_id)
            if status:
                query = query.eq("status", status)

            # Order and limit
            query = query.order("order_date", desc=True)
            if limit:
                query = query.limit(limit)

            result = query.execute()
            orders = result.data or []

            # Get basic order items for each order
            for order in orders:
                items_result = (
                    self.supabase.table("order_items")
                    .select("calculated_pieces")
                    .eq("order_id", order["id"])
                    .execute()
                )

                order["order_items"] = items_result.data or []

                # Extract related data
                if order.get("parties"):
                    order["party_name"] = order["parties"]["party_name"]
                if order.get("qualities"):
                    order["quality_name"] = order["qualities"]["quality_name"]

            self.logger.debug(f"Search found {len(orders)} orders")

            return orders

        except Exception as e:
            self.logger.error(f"Error searching orders: {str(e)}")
            raise

    async def get_order_statistics(self) -> Dict:
        """Get order statistics for dashboard"""
        try:
            self.logger.debug("Fetching order statistics")

            # Get total counts by status
            total_orders = await self.count()
            pending_orders = await self.count({"status": "pending"})
            completed_orders = await self.count({"status": "completed"})

            # Get recent orders
            recent_orders = await self.get_all_orders_with_details(limit=5)

            # Calculate total value (this would require more complex aggregation)
            # For now, we'll set it to 0 and calculate it in the service layer
            total_value = 0

            # Get top parties (placeholder - would need aggregation)
            top_parties = []

            stats = {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "completed_orders": completed_orders,
                "total_value": total_value,
                "recent_orders": recent_orders[:5],
                "top_parties": top_parties,
            }

            self.logger.debug(f"Order statistics: {stats}")

            return stats

        except Exception as e:
            self.logger.error(f"Error fetching order statistics: {str(e)}")
            raise
