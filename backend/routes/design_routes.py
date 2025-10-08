"""
Design API Routes - Endpoints for design tracking and beam allocation
Layer 1: Presentation Layer
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from models.schemas.design import (
    BeamConfigResponse,
    CompleteBeamSummaryResponse,
    DesignSetTrackingResponse,
    DesignWiseAllocationResponse,
)
from services.design_service import DesignService

router = APIRouter()


def get_design_service() -> DesignService:
    """Dependency injection for design service"""
    return DesignService()


# ============================================
# Design Set Tracking Endpoints
# ============================================


@router.get(
    "/orders/{order_id}/tracking", response_model=List[DesignSetTrackingResponse]
)
async def get_design_tracking(
    order_id: int,
    design_number: Optional[str] = Query(None, description="Filter by specific design"),
    design_service: DesignService = Depends(get_design_service),
):
    """
    Get design set tracking for an order

    Shows total sets, allocated sets, and remaining sets for each design
    """
    return await design_service.get_design_tracking(order_id, design_number)


@router.get("/orders/{order_id}/designs", response_model=List[str])
async def get_designs_for_order(
    order_id: int,
    design_service: DesignService = Depends(get_design_service),
):
    """Get list of design numbers for an order"""
    return await design_service.get_designs_by_order(order_id)


# ============================================
# Beam Configuration Endpoints
# ============================================


@router.get("/orders/{order_id}/beam-config", response_model=List[BeamConfigResponse])
async def get_beam_config(
    order_id: int,
    design_number: Optional[str] = Query(None, description="Filter by specific design"),
    design_service: DesignService = Depends(get_design_service),
):
    """
    Get beam configurations for designs in an order

    Shows beam color and multiplier for each design (e.g., B-2, F-1, RB-1)
    """
    return await design_service.get_beam_config(order_id, design_number)


# ============================================
# Design-Wise Allocation Reports (NEW)
# ============================================


@router.get("/allocation/design-wise", response_model=DesignWiseAllocationResponse)
async def get_design_wise_allocation(
    order_id: Optional[int] = Query(None, description="Filter by specific order"),
    party_id: Optional[int] = Query(None, description="Filter by specific party"),
    design_service: DesignService = Depends(get_design_service),
):
    """
    Get design-wise beam allocation table (NEW TABLE)

    Shows each design separately with:
    - Remaining sets
    - Beam pieces breakdown (B: X pieces, F: Y pieces, etc.)
    - Party and quality info

    This is the NEW design-wise detail table requested.
    """
    return await design_service.get_design_wise_allocation(order_id, party_id)


@router.get("/allocation/complete-summary", response_model=CompleteBeamSummaryResponse)
async def get_complete_beam_summary(
    design_service: DesignService = Depends(get_design_service),
):
    """
    Get complete beam allocation table (ALL DESIGNS AGGREGATED)

    This is the EXISTING beam allocation table that shows total pieces
    across all designs, grouped by quality.

    Kept alongside the new design-wise table as requested.
    """
    return await design_service.get_complete_beam_summary()


# ============================================
# Validation Endpoint
# ============================================


@router.get("/orders/{order_id}/designs/{design_number}/validate-allocation")
async def validate_design_allocation(
    order_id: int,
    design_number: str,
    requested_sets: int = Query(..., gt=0, description="Number of sets to allocate"),
    design_service: DesignService = Depends(get_design_service),
):
    """
    Validate if requested sets can be allocated to a design

    Useful for frontend validation before creating lot
    """
    return await design_service.validate_design_allocation(
        order_id, design_number, requested_sets
    )
