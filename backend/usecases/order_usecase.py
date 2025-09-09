"""
Order Use Cases - Business Logic
"""

from typing import Any, Dict, List

from models.domain.order import Order
from repositories.color_repository import ColorRepository
from repositories.order_repository import OrderRepository


class OrderUseCase:
    """Order business logic"""

    def __init__(self):
        self.order_repository = OrderRepository()
        self.color_repository = ColorRepository()

    async def create_order(self, order_data: dict) -> Order:
        """Create new order with validation and calculations"""
        # Validate party and quality exist (you may want to add these checks)

        # Validate design numbers are unique
        design_numbers = order_data["design_numbers"]
        if len(design_numbers) != len(set(design_numbers)):
            raise ValueError("Duplicate design numbers are not allowed")

        # Validate ground colors and beam colors exist
        await self._validate_colors(order_data["ground_colors"])

        # Create order with calculations
        return await self.order_repository.create(order_data)

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get order by ID with complete details"""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Get related data
        cuts = await self.order_repository.get_order_cuts(order_id)
        design_numbers = await self.order_repository.get_design_numbers(order_id)
        order_items = await self.order_repository.get_order_items(order_id)

        # Calculate beam summary and colors
        beam_summary, beam_colors = await self._calculate_beam_details(
            order_items, order.total_designs, order_data.get("pieces_per_color", 0)
        )

        # Build response
        order_dict = order.to_dict()
        order_dict.update(
            {
                "cuts": cuts,
                "design_numbers": design_numbers,
                "beam_summary": beam_summary,
                "beam_colors": beam_colors,
            }
        )

        return order_dict

    async def update_order(self, order_id: int, update_data: dict) -> Order:
        """Update order with validation"""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Validate design numbers if provided
        if "design_numbers" in update_data:
            design_numbers = update_data["design_numbers"]
            if len(design_numbers) != len(set(design_numbers)):
                raise ValueError("Duplicate design numbers are not allowed")

        # Validate colors if provided
        if "ground_colors" in update_data:
            await self._validate_colors(update_data["ground_colors"])

        return await self.order_repository.update(order_id, update_data)

    async def delete_order(self, order_id: int) -> bool:
        """Delete order"""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        return await self.order_repository.delete(order_id)

    async def list_orders(self, page: int = 1, page_size: int = 20) -> dict:
        """List orders with pagination"""
        offset = (page - 1) * page_size
        orders = await self.order_repository.get_all(limit=page_size, offset=offset)
        total_count = await self.order_repository.count_all()

        # Convert to list items
        order_list = []
        for order in orders:
            order_dict = order.to_dict()
            # You may want to add party_name and quality_name here
            order_list.append(order_dict)

        return {
            "orders": order_list,
            "page": page,
            "page_size": page_size,
            "total": total_count,
        }

    async def search_orders(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search orders"""
        orders = await self.order_repository.search(query, limit)
        return [order.to_dict() for order in orders]

    async def calculate_beam_preview(
        self,
        ground_colors: List[Dict],
        design_numbers: List[str],
        pieces_per_color: int,
    ) -> Dict[str, Any]:
        """Calculate beam summary preview for order creation"""
        total_designs = len(design_numbers)

        # Create mock order items for calculation
        mock_items = []
        for design in design_numbers:
            for ground_color in ground_colors:
                mock_item = {
                    "design_number": design,
                    "ground_color_id": ground_color["ground_color_id"],
                    "beam_color_id": ground_color["beam_color_id"],
                    "pieces_per_color": pieces_per_color,
                }
                mock_items.append(mock_item)

        # Convert to domain objects for calculation
        from models.domain.order import OrderItem

        order_items = [OrderItem.from_dict(item) for item in mock_items]

        # Calculate beam details
        beam_summary, beam_colors = await self._calculate_beam_details(
            order_items, total_designs, pieces_per_color
        )

        # Calculate totals
        total_pieces = sum([color["calculated_pieces"] for color in beam_colors])

        return {
            "total_designs": total_designs,
            "beam_summary": beam_summary,
            "beam_colors": beam_colors,
            "total_pieces": total_pieces,
        }

    async def _validate_colors(self, ground_colors: List[Dict]) -> None:
        """Validate that ground colors and beam colors exist"""
        color_ids = set()
        for ground_color in ground_colors:
            color_ids.add(ground_color["ground_color_id"])
            color_ids.add(ground_color["beam_color_id"])

        # Check if all colors exist
        for color_id in color_ids:
            color = await self.color_repository.get_by_id(color_id)
            if not color:
                raise ValueError(f"Color with ID {color_id} not found")

    async def _calculate_beam_details(
        self, order_items: List, total_designs: int, pieces_per_color: int
    ) -> tuple:
        """Calculate beam summary and detailed beam colors"""
        # Count beam color occurrences
        beam_counts = {}
        for item in order_items:
            beam_color_id = item.beam_color_id
            beam_counts[beam_color_id] = beam_counts.get(beam_color_id, 0) + 1

        # Get color details and calculate pieces
        beam_colors = []
        beam_summary = {}

        for color_id, count in beam_counts.items():
            color = await self.color_repository.get_by_id(color_id)
            if color:
                calculated_pieces = pieces_per_color * count * total_designs

                beam_colors.append(
                    {
                        "color_code": color.color_code,
                        "color_name": color.color_name,
                        "selection_count": count,
                        "calculated_pieces": calculated_pieces,
                    }
                )

                beam_summary[color.color_code] = count

        return beam_summary, beam_colors
