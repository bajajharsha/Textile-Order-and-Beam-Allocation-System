"""
Lot Controller - API request handlers
"""

from typing import Dict, List, Optional

from models.schemas.lot import (
    LotCreate,
    LotRegisterResponse,
    LotResponse,
    LotUpdate,
    OrderItemStatusResponse,
)
from services.lot_service import LotService


class LotController:
    """Lot API handlers"""

    def __init__(self):
        self.lot_service = LotService()

    async def create_lot(self, lot_data: LotCreate) -> LotResponse:
        """Handle create lot request"""
        return await self.lot_service.create_lot(lot_data)

    async def get_lot(self, lot_id: int) -> LotResponse:
        """Handle get lot request"""
        return await self.lot_service.get_lot_by_id(lot_id)

    async def list_lots(self, page: int = 1, page_size: int = 20) -> Dict:
        """Handle list lots request"""
        return await self.lot_service.get_all_lots(page, page_size)

    async def update_lot(self, lot_id: int, update_data: LotUpdate) -> LotResponse:
        """Handle update lot request"""
        return await self.lot_service.update_lot(lot_id, update_data)

    async def delete_lot(self, lot_id: int) -> Dict:
        """Handle delete lot request"""
        return await self.lot_service.delete_lot(lot_id)

    async def get_partywise_detail(self, party_id: Optional[int] = None) -> Dict:
        """Handle partywise detail (red book) request"""
        return await self.lot_service.get_partywise_detail(party_id)

    async def get_lot_register(
        self,
        page: int = 1,
        page_size: int = 20,
        lot_register_type: Optional[str] = None,
    ) -> LotRegisterResponse:
        """Handle lot register request"""
        return await self.lot_service.get_lot_register(
            page, page_size, lot_register_type
        )

    async def get_order_allocation_status(
        self, order_id: Optional[int] = None
    ) -> List[OrderItemStatusResponse]:
        """Handle order allocation status request"""
        return await self.lot_service.get_order_allocation_status(order_id)

    async def get_beam_summary_with_allocation(self) -> Dict:
        """Handle beam summary with allocation request"""
        return await self.lot_service.get_beam_summary_with_allocation()

    async def get_available_allocations(
        self,
        party_id: Optional[int] = None,
        quality_id: Optional[int] = None,
    ) -> List[OrderItemStatusResponse]:
        """Handle available allocations request"""
        return await self.lot_service.get_available_allocations(party_id, quality_id)

    async def initialize_order_status(self, order_id: int) -> Dict:
        """Handle initialize order status request"""
        return await self.lot_service.initialize_order_status(order_id)

    async def update_lot_field(self, lot_id: int, field: str, value: str) -> Dict:
        """Handle update lot field request (for inline editing)"""
        return await self.lot_service.update_lot_field(lot_id, field, value)

    async def create_lot_from_register(self, lot_data: dict) -> Dict:
        """Handle create lot from register request"""
        return await self.lot_service.create_lot_from_register(lot_data)

    async def create_lot_for_design(self, lot_data: dict) -> Dict:
        """Handle create lot for specific design request"""
        return await self.lot_service.create_lot_for_design(lot_data)
