"""
Order API Routes
"""

from typing import List

from controllers.order_controller import OrderController
from fastapi import APIRouter, Depends, Query
from models.schemas.order import OrderCreate, OrderUpdate
from pydantic import BaseModel

router = APIRouter()


# Beam preview request model
class BeamPreviewRequest(BaseModel):
    """Schema for beam calculation preview"""

    ground_colors: List[dict]
    design_numbers: List[str]
    pieces_per_color: int

    class Config:
        from_attributes = True


@router.post("/")
async def create_order(
    order_data: OrderCreate,
    order_controller: OrderController = Depends(OrderController),
):
    """Create new order"""
    return await order_controller.create_order(order_data.dict())


@router.get("/{order_id}")
async def get_order(order_id: int, order_controller: OrderController = Depends()):
    """Get order by ID"""
    return await order_controller.get_order(order_id)


@router.put("/{order_id}")
async def update_order(
    order_id: int,
    update_data: OrderUpdate,
    order_controller: OrderController = Depends(OrderController),
):
    """Update order"""
    return await order_controller.update_order(
        order_id, update_data.dict(exclude_unset=True)
    )


@router.delete("/{order_id}")
async def delete_order(order_id: int, order_controller: OrderController = Depends()):
    """Delete order"""
    return await order_controller.delete_order(order_id)


@router.get("/")
async def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    order_controller: OrderController = Depends(OrderController),
):
    """List all orders with pagination"""
    return await order_controller.list_orders(page, page_size)


@router.get("/search/")
async def search_orders(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    order_controller: OrderController = Depends(OrderController),
):
    """Search orders"""
    return await order_controller.search_orders(q, limit)


@router.post("/preview/")
async def calculate_beam_preview(
    preview_data: BeamPreviewRequest,
    order_controller: OrderController = Depends(OrderController),
):
    """Calculate beam summary preview before saving order"""
    return await order_controller.calculate_beam_preview(
        preview_data.ground_colors,
        preview_data.design_numbers,
        preview_data.pieces_per_color,
    )
