"""
Lot Use Case - Business logic for lot management
"""

from typing import List, Optional

from config.logging import get_logger
from repositories.color_repository import ColorRepository
from repositories.lot_repository import LotRepository
from repositories.order_repository import OrderRepository


class LotUseCase:
    """Lot business logic"""

    def __init__(self):
        self.lot_repository = LotRepository()
        self.order_repository = OrderRepository()
        self.color_repository = ColorRepository()
        self.logger = get_logger("usecases.lot")

    async def create_lot(self, lot_data: dict) -> dict:
        """Create new lot with allocations"""
        try:
            self.logger.info(f"Creating lot for party {lot_data['party_id']}")

            # Validate allocations
            await self._validate_allocations(lot_data["allocations"])

            # Create lot
            lot = await self.lot_repository.create_lot(
                lot_data, lot_data["allocations"]
            )

            # Get lot with details
            lot_with_details = await self.lot_repository.get_lot_with_details(lot.id)

            self.logger.info(f"Successfully created lot {lot.lot_number}")
            return lot_with_details

        except Exception as e:
            self.logger.error(f"Error creating lot: {str(e)}")
            raise

    async def get_lot_details(self, lot_id: int) -> Optional[dict]:
        """Get lot details with allocations"""
        try:
            return await self.lot_repository.get_lot_with_details(lot_id)
        except Exception as e:
            self.logger.error(f"Error getting lot details: {str(e)}")
            raise

    async def get_all_lots(self, page: int = 1, page_size: int = 20) -> dict:
        """Get all lots with pagination"""
        try:
            offset = (page - 1) * page_size
            lots = await self.lot_repository.get_all_lots(
                limit=page_size, offset=offset
            )
            total_count = await self.lot_repository.count_lots()

            return {
                "lots": lots,
                "page": page,
                "page_size": page_size,
                "total": total_count,
            }

        except Exception as e:
            self.logger.error(f"Error getting lots: {str(e)}")
            raise

    async def update_lot(self, lot_id: int, update_data: dict) -> Optional[dict]:
        """Update lot details"""
        try:
            # Update lot
            updated_lot = await self.lot_repository.update_lot(lot_id, update_data)
            if not updated_lot:
                return None

            # Get updated lot with details
            return await self.lot_repository.get_lot_with_details(lot_id)

        except Exception as e:
            self.logger.error(f"Error updating lot: {str(e)}")
            raise

    async def delete_lot(self, lot_id: int) -> bool:
        """Delete lot and its allocations"""
        try:
            return await self.lot_repository.delete_lot(lot_id)
        except Exception as e:
            self.logger.error(f"Error deleting lot: {str(e)}")
            raise

    async def get_partywise_detail(self, party_id: Optional[int] = None) -> dict:
        """Get partywise detail (red book) report"""
        try:
            details = await self.lot_repository.get_partywise_detail(party_id)

            # Group by party
            party_groups = {}
            for item in details:
                party_name = item["party_name"]
                if party_name not in party_groups:
                    party_groups[party_name] = {
                        "party_name": party_name,
                        "items": [],
                        "total_remaining_pieces": 0,
                        "total_allocated_pieces": 0,
                        "total_value": 0,
                    }

                party_groups[party_name]["items"].append(item)
                party_groups[party_name]["total_remaining_pieces"] += item.get(
                    "sets_pcs", 0
                )

                # Calculate total value
                rate = float(item.get("rate", 0))
                pieces = item.get("sets_pcs", 0)
                party_groups[party_name]["total_value"] += rate * pieces

            # Convert to list
            result = list(party_groups.values())

            return {
                "parties": result,
                "total_parties": len(result),
                "grand_total_pieces": sum(p["total_remaining_pieces"] for p in result),
            }

        except Exception as e:
            self.logger.error(f"Error getting partywise detail: {str(e)}")
            raise

    async def get_lot_register(self, page: int = 1, page_size: int = 20) -> dict:
        """Get lot register report"""
        try:
            offset = (page - 1) * page_size
            items = await self.lot_repository.get_lot_register(
                limit=page_size, offset=offset
            )
            total_count = await self.lot_repository.count_lots()

            # Calculate totals
            total_pieces = sum(item.get("total_pieces", 0) for item in items)
            total_delivered = sum(
                item.get("actual_pieces", 0) or 0
                for item in items
                if item.get("status") == "DELIVERED"
            )

            return {
                "items": items,
                "total_lots": len(set(item["lot_id"] for item in items)),
                "total_pieces": total_pieces,
                "total_delivered": total_delivered,
                "page": page,
                "page_size": page_size,
                "total": total_count,
            }

        except Exception as e:
            self.logger.error(f"Error getting lot register: {str(e)}")
            raise

    async def get_order_allocation_status(
        self, order_id: Optional[int] = None
    ) -> List[dict]:
        """Get order item allocation status"""
        try:
            return await self.lot_repository.get_order_item_status(order_id)
        except Exception as e:
            self.logger.error(f"Error getting order allocation status: {str(e)}")
            raise

    async def get_beam_summary_with_allocation(self) -> dict:
        """Get beam summary with allocation details"""
        try:
            summary = await self.lot_repository.get_beam_summary_with_allocation()

            # Group by quality
            quality_groups = {}
            for item in summary:
                quality_name = item["quality_name"]
                if quality_name not in quality_groups:
                    quality_groups[quality_name] = {
                        "quality_name": quality_name,
                        "items": [],
                        "total_pieces": 0,
                        "allocated_pieces": 0,
                        "remaining_pieces": 0,
                    }

                quality_groups[quality_name]["items"].append(item)
                quality_groups[quality_name]["total_pieces"] += item["total_pieces"]
                quality_groups[quality_name]["allocated_pieces"] += item[
                    "allocated_pieces"
                ]
                quality_groups[quality_name]["remaining_pieces"] += item[
                    "remaining_pieces"
                ]

            return {
                "qualities": list(quality_groups.values()),
                "summary": await self.lot_repository.get_allocation_summary(),
            }

        except Exception as e:
            self.logger.error(f"Error getting beam summary with allocation: {str(e)}")
            raise

    async def get_available_allocations(
        self, party_id: Optional[int] = None, quality_id: Optional[int] = None
    ) -> List[dict]:
        """Get available items for allocation (items with remaining pieces > 0)"""
        try:
            # Get order item status with remaining pieces
            all_status = await self.lot_repository.get_order_item_status()

            # Filter items with remaining pieces
            available_items = [
                item for item in all_status if item["remaining_pieces"] > 0
            ]

            # Apply filters
            if party_id:
                available_items = [
                    item for item in available_items if item.get("party_id") == party_id
                ]

            if quality_id:
                available_items = [
                    item
                    for item in available_items
                    if item.get("quality_id") == quality_id
                ]

            return available_items

        except Exception as e:
            self.logger.error(f"Error getting available allocations: {str(e)}")
            raise

    async def _validate_allocations(self, allocations: List[dict]) -> None:
        """Validate allocation data"""
        for allocation in allocations:
            order_id = allocation["order_id"]
            design_number = allocation["design_number"]
            ground_color_name = allocation["ground_color_name"]
            allocated_pieces = allocation["allocated_pieces"]

            # Check if order exists
            order = await self.order_repository.get_by_id(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")

            # Get current status for this item
            status_items = await self.lot_repository.get_order_item_status(order_id)
            matching_status = None

            for status in status_items:
                if (
                    status["design_number"] == design_number
                    and status["ground_color_name"] == ground_color_name
                ):
                    matching_status = status
                    break

            if not matching_status:
                raise ValueError(
                    f"No status found for order {order_id}, design {design_number}, color {ground_color_name}"
                )

            # Check if enough pieces are available
            if allocated_pieces > matching_status["remaining_pieces"]:
                raise ValueError(
                    f"Cannot allocate {allocated_pieces} pieces. Only {matching_status['remaining_pieces']} pieces remaining for order {order_id}, design {design_number}, color {ground_color_name}"
                )

            # Validate beam color
            if allocation["beam_color_id"] != matching_status["beam_color_id"]:
                raise ValueError(
                    f"Beam color mismatch for order {order_id}, design {design_number}, color {ground_color_name}"
                )

    async def initialize_order_status(self, order_id: int) -> None:
        """Initialize order item status after order creation"""
        try:
            await self.lot_repository.initialize_order_item_status(order_id)
            self.logger.info(f"Initialized order item status for order {order_id}")
        except Exception as e:
            self.logger.error(f"Error initializing order status: {str(e)}")
            raise

    async def update_lot_field(self, lot_id: int, field: str, value: str) -> bool:
        """Update a specific field of a lot (for inline editing)"""
        try:
            success = await self.lot_repository.update_lot_field(lot_id, field, value)
            if success:
                self.logger.info(f"Updated lot {lot_id} field {field} to {value}")
            return success
        except Exception as e:
            self.logger.error(f"Error updating lot field: {str(e)}")
            raise

    async def create_lot_from_register(
        self,
        order_id: int,
        lot_number: str,
        lot_date: str,
        party_id: int,
        quality_id: int,
    ) -> dict:
        """Create a lot when lot number is entered in the register"""
        try:
            created_lot = await self.lot_repository.create_lot_from_register(
                order_id, lot_number, lot_date, party_id, quality_id
            )
            self.logger.info(f"Created lot {lot_number} from order {order_id}")
            return created_lot
        except Exception as e:
            self.logger.error(f"Error creating lot from register: {str(e)}")
            raise

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
        try:
            created_lot = await self.lot_repository.create_lot_for_design(
                order_id,
                design_number,
                lot_number,
                lot_date,
                party_id,
                quality_id,
                bill_number,
                actual_pieces,
                delivery_date,
            )
            self.logger.info(
                f"Created lot {lot_number} for design {design_number} from order {order_id}"
            )
            return created_lot
        except Exception as e:
            self.logger.error(f"Error creating lot for design: {str(e)}")
            raise
