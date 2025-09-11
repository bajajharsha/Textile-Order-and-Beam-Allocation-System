"""
Lot API Routes
"""

from typing import Dict, List, Optional

from controllers.lot_controller import LotController
from fastapi import APIRouter, Depends, Query
from models.schemas.lot import (
    LotCreate,
    LotRegisterResponse,
    LotResponse,
    LotUpdate,
    OrderItemStatusResponse,
)

router = APIRouter(tags=["lots"])


@router.post("/", response_model=LotResponse)
async def create_lot(
    lot_data: LotCreate,
    lot_controller: LotController = Depends(LotController),
):
    """Create new lot with allocations"""
    return await lot_controller.create_lot(lot_data)


@router.get("/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: int,
    lot_controller: LotController = Depends(LotController),
):
    """Get lot by ID"""
    return await lot_controller.get_lot(lot_id)


@router.get("/", response_model=Dict)
async def list_lots(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    lot_controller: LotController = Depends(LotController),
):
    """List all lots with pagination"""
    return await lot_controller.list_lots(page, page_size)


@router.put("/{lot_id}", response_model=LotResponse)
async def update_lot(
    lot_id: int,
    update_data: LotUpdate,
    lot_controller: LotController = Depends(LotController),
):
    """Update lot"""
    return await lot_controller.update_lot(lot_id, update_data)


@router.delete("/{lot_id}")
async def delete_lot(
    lot_id: int,
    lot_controller: LotController = Depends(LotController),
):
    """Delete lot"""
    return await lot_controller.delete_lot(lot_id)


@router.get("/reports/partywise-detail")
async def get_partywise_detail(
    party_id: Optional[int] = Query(None, description="Filter by party ID"),
    lot_controller: LotController = Depends(LotController),
):
    """Get partywise detail (red book) report"""
    return await lot_controller.get_partywise_detail(party_id)


@router.get("/reports/lot-register", response_model=LotRegisterResponse)
async def get_lot_register(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    lot_controller: LotController = Depends(LotController),
):
    """Get lot register report"""
    return await lot_controller.get_lot_register(page, page_size)


@router.get("/reports/beam-summary-allocation")
async def get_beam_summary_with_allocation(
    lot_controller: LotController = Depends(LotController),
):
    """Get beam summary with allocation details"""
    return await lot_controller.get_beam_summary_with_allocation()


@router.get("/allocation/status", response_model=List[OrderItemStatusResponse])
async def get_order_allocation_status(
    order_id: Optional[int] = Query(None, description="Filter by order ID"),
    lot_controller: LotController = Depends(LotController),
):
    """Get order item allocation status"""
    return await lot_controller.get_order_allocation_status(order_id)


@router.get("/allocation/available", response_model=List[OrderItemStatusResponse])
async def get_available_allocations(
    party_id: Optional[int] = Query(None, description="Filter by party ID"),
    quality_id: Optional[int] = Query(None, description="Filter by quality ID"),
    lot_controller: LotController = Depends(LotController),
):
    """Get available items for allocation"""
    return await lot_controller.get_available_allocations(party_id, quality_id)


@router.post("/allocation/initialize/{order_id}")
async def initialize_order_status(
    order_id: int,
    lot_controller: LotController = Depends(LotController),
):
    """Initialize order item status after order creation"""
    return await lot_controller.initialize_order_status(order_id)


@router.patch("/{lot_id}/field/{field}")
async def update_lot_field(
    lot_id: int,
    field: str,
    value: str,
    lot_controller: LotController = Depends(LotController),
):
    """Update a specific field of a lot (for inline editing)"""
    return await lot_controller.update_lot_field(lot_id, field, value)


@router.post("/create-from-register")
async def create_lot_from_register(
    lot_data: dict,
    lot_controller: LotController = Depends(LotController),
):
    """Create a lot when lot number is entered in the register"""
    return await lot_controller.create_lot_from_register(lot_data)
