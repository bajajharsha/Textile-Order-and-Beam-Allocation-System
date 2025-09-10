"""
Order Use Cases - Business Logic
"""

import logging
from typing import Any, Dict, List

from models.domain.order import Order
from repositories.color_repository import ColorRepository
from repositories.order_repository import OrderRepository


class OrderUseCase:
    """Order business logic"""

    def __init__(self):
        self.order_repository = OrderRepository()
        self.color_repository = ColorRepository()
        self.logger = logging.getLogger(__name__)

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
            order_items, order.total_designs
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
        units: int,
        ground_colors: List[Dict],
        design_numbers: List[str],
    ) -> Dict[str, Any]:
        """Calculate beam summary preview for order creation using new formula"""
        total_designs = len(design_numbers)

        # Count beam color occurrences
        beam_color_counts = {}
        for ground_color in ground_colors:
            beam_color_id = ground_color["beam_color_id"]
            beam_color_counts[beam_color_id] = (
                beam_color_counts.get(beam_color_id, 0) + 1
            )

        # Create beam summary using new calculation
        beam_colors = []
        beam_summary = {}

        for beam_color_id, count in beam_color_counts.items():
            # Get color information
            color = await self.color_repository.get_by_id(beam_color_id)
            if color:
                # Calculate pieces: Units × Total Designs × Beam Color Count
                calculated_pieces = units * total_designs * count

                beam_color_info = {
                    "beam_color_id": beam_color_id,
                    "beam_color_name": f"{color.color_name} ({color.color_code})",
                    "total_pieces": calculated_pieces,
                }
                beam_colors.append(beam_color_info)
                beam_summary[color.color_code] = count

        # Calculate total pieces
        total_pieces = sum([color["total_pieces"] for color in beam_colors])

        return {
            "total_designs": total_designs,
            "beam_summary": beam_colors,  # Return the beam colors array for frontend
            "total_pieces": total_pieces,
        }

    async def _validate_colors(self, ground_colors: List[Dict]) -> None:
        """Validate that beam colors exist"""
        color_ids = set()
        for ground_color in ground_colors:
            # Only validate beam_color_id since ground_color_name is manual entry
            color_ids.add(ground_color["beam_color_id"])

        # Check if all colors exist
        for color_id in color_ids:
            color = await self.color_repository.get_by_id(color_id)
            if not color:
                raise ValueError(f"Color with ID {color_id} not found")

    async def get_beam_details(self) -> List[Dict]:
        """Get beam allocation details for all orders grouped by quality"""
        try:
            # Get all active orders with their related data
            orders = await self.order_repository.get_all_orders()

            if not orders:
                return []

            # Group orders by quality
            quality_groups = {}

            for order in orders:
                quality_name = (
                    order.quality_name
                    if hasattr(order, "quality_name")
                    else f"Quality {order.quality_id}"
                )
                party_name = (
                    order.party_name
                    if hasattr(order, "party_name")
                    else f"Party {order.party_id}"
                )

                if quality_name not in quality_groups:
                    quality_groups[quality_name] = []

                # Get order items to calculate beam colors
                order_items = await self.order_repository.get_order_items(order.id)

                # Calculate beam color counts
                beam_color_counts = {}
                color_per_beam_parts = []

                for item in order_items:
                    beam_color_id = item.beam_color_id
                    beam_color_counts[beam_color_id] = (
                        beam_color_counts.get(beam_color_id, 0) + 1
                    )

                # Create color per beam string (e.g., "R-2,F-1,B-3")
                for color_id, count in beam_color_counts.items():
                    color = await self.color_repository.get_by_id(color_id)
                    if color:
                        color_per_beam_parts.append(f"{color.color_code}-{count}")

                color_per_beam = f"({','.join(color_per_beam_parts)})"

                # Calculate pieces for each color using the formula:
                # Units × Total Designs × Beam Color Count
                colors = {
                    "red": 0,
                    "firozi": 0,
                    "gold": 0,
                    "royal_blue": 0,
                    "black": 0,
                    "white": 0,
                    "yellow": 0,
                    "green": 0,
                    "purple": 0,
                    "orange": 0,
                }

                # Map color codes to color names
                color_mapping = {
                    "R": "red",
                    "F": "firozi",
                    "G": "gold",
                    "RB": "royal_blue",
                    "B": "black",
                    "W": "white",
                    "Y": "yellow",
                    "GR": "green",
                    "P": "purple",
                    "O": "orange",
                }

                total_pieces = 0
                for color_id, count in beam_color_counts.items():
                    color = await self.color_repository.get_by_id(color_id)
                    if color and color.color_code in color_mapping:
                        color_name = color_mapping[color.color_code]
                        pieces = order.units * order.total_designs * count
                        colors[color_name] = pieces
                        total_pieces += pieces

                # Add to quality group
                quality_groups[quality_name].append(
                    {
                        "party_name": party_name,
                        "quality_name": quality_name,
                        "color_per_beam": color_per_beam,
                        "colors": colors,
                        "total": total_pieces,
                    }
                )

            # Convert to the expected format
            result = []
            for quality_name, items in quality_groups.items():
                result.append({"quality_name": quality_name, "items": items})

            return result

        except Exception as e:
            self.logger.error(f"Error getting beam details: {str(e)}")
            return []

    async def _calculate_beam_details(
        self, order_items: List, total_designs: int
    ) -> tuple:
        """Calculate beam summary and detailed beam colors"""
        # This method is now deprecated as we use the new calculation logic
        # Return empty data for backward compatibility
        return {}, []
