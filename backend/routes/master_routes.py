"""
Master data API routes
Layer 1: Presentation Layer - Route Definitions
"""

from typing import Dict, List

from controllers.master_controller import MasterDataController
from fastapi import APIRouter, Path, status
from models.base import APIResponse
from models.order import Color, Quality

# Create router instance
router = APIRouter(prefix="/master", tags=["master-data"])

# Initialize controller
master_controller = MasterDataController()


# Routes
@router.get(
    "/colors",
    response_model=APIResponse[List[Color]],
    summary="Get all colors",
    description="Retrieve all active colors for dropdowns and forms",
)
async def get_all_colors():
    """Get all active colors"""
    return await master_controller.get_all_colors()


@router.get(
    "/qualities",
    response_model=APIResponse[List[Quality]],
    summary="Get all qualities",
    description="Retrieve all active qualities for dropdowns and forms",
)
async def get_all_qualities():
    """Get all active qualities"""
    return await master_controller.get_all_qualities()


@router.get(
    "/all",
    response_model=APIResponse[Dict],
    summary="Get all master data",
    description="Retrieve all master data (colors, qualities) in one call",
)
async def get_all_master_data():
    """Get all master data for forms and dropdowns"""
    return await master_controller.get_all_master_data()


@router.get(
    "/colors/{color_id}",
    response_model=APIResponse[Color],
    summary="Get color by ID",
    description="Retrieve a specific color by its ID",
)
async def get_color_by_id(color_id: int = Path(..., description="Color ID", gt=0)):
    """Get color by ID"""
    return await master_controller.get_color_by_id(color_id)


@router.get(
    "/qualities/{quality_id}",
    response_model=APIResponse[Quality],
    summary="Get quality by ID",
    description="Retrieve a specific quality by its ID",
)
async def get_quality_by_id(
    quality_id: int = Path(..., description="Quality ID", gt=0),
):
    """Get quality by ID"""
    return await master_controller.get_quality_by_id(quality_id)


@router.post(
    "/initialize",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Initialize default master data",
    description="Initialize master data with default colors and qualities",
)
async def initialize_default_data():
    """Initialize master data with default values"""
    return await master_controller.initialize_default_data()
