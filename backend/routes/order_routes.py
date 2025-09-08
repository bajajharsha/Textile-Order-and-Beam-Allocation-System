"""
Order API routes
Layer 1: Presentation Layer - Route Definitions
"""

from controllers.order_controller import OrderController
from fastapi import APIRouter, Path, status
from models.base import APIResponse
from models.order import OrderCreate, OrderResponse, OrderUpdate

# Create router instance
router = APIRouter(prefix="/orders", tags=["orders"])

# Initialize controller
order_controller = OrderController()


# Routes
@router.post(
    "/",
    response_model=APIResponse[OrderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new order",
    description="Create a new order with automatic beam calculations",
)
async def create_order(order_data: OrderCreate):
    """Create a new order"""
    return await order_controller.create_order(order_data)


@router.get(
    "/{order_id}",
    response_model=APIResponse[OrderResponse],
    summary="Get order by ID",
    description="Retrieve a specific order by its ID with all details",
)
async def get_order_by_id(order_id: int = Path(..., description="Order ID", gt=0)):
    """Get order by ID"""
    return await order_controller.get_order_by_id(order_id)


@router.get(
    "/",
    response_model=APIResponse[list[OrderResponse]],
    summary="Get all orders",
    description="Retrieve all orders with optional filtering and pagination",
)
async def get_all_orders():
    """Get all orders with optional filtering"""
    return await order_controller.get_all_orders()


@router.put(
    "/{order_id}",
    response_model=APIResponse[OrderResponse],
    summary="Update order",
    description="Update an existing order's information",
)
async def update_order(
    order_data: OrderUpdate,
    order_id: int = Path(..., description="Order ID", gt=0),
):
    """Update existing order"""
    return await order_controller.update_order(order_id, order_data)


@router.get(
    "/search/",
    response_model=APIResponse[list[OrderResponse]],
    summary="Search orders",
    description="Search orders by order number, party name, design numbers, or other criteria",
)
async def search_orders():
    """Search orders based on criteria"""
    return await order_controller.search_orders()


@router.get(
    "/reports/quality-wise-summary",
    response_model=APIResponse[dict],
    summary="Get quality-wise beam summary",
    description="Generate quality-wise beam summary for reporting",
)
async def get_quality_wise_summary():
    """Get quality-wise beam summary for reporting"""
    return await order_controller.get_quality_wise_summary()


@router.get(
    "/party/{party_id}",
    response_model=APIResponse[list[OrderResponse]],
    summary="Get orders by party",
    description="Get all orders for a specific party",
)
async def get_orders_by_party(party_id: int = Path(..., description="Party ID", gt=0)):
    """Get all orders for a specific party"""
    return await order_controller.get_orders_by_party(party_id)


@router.get(
    "/stats/statistics",
    response_model=APIResponse[dict],
    summary="Get order statistics",
    description="Get order statistics for dashboard display",
)
async def get_order_statistics():
    """Get order statistics for dashboard"""
    return await order_controller.get_order_statistics()


@router.post(
    "/validate/data",
    response_model=APIResponse[dict],
    summary="Validate order data",
    description="Validate order data for frontend form validation",
)
async def validate_order_data(order_data: dict):
    """Validate order data for frontend"""
    return await order_controller.validate_order_data(order_data)


@router.get(
    "/{order_id}/calculations",
    response_model=APIResponse[list[dict]],
    summary="Get order calculation details",
    description="Get detailed calculation breakdown for an order",
)
async def get_order_calculation_details(
    order_id: int = Path(..., description="Order ID", gt=0),
):
    """Get detailed calculation breakdown for an order"""
    return await order_controller.get_order_calculation_details(order_id)
