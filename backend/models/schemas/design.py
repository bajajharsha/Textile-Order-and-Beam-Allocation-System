"""
Design schemas for API requests and responses
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# ============================================
# Beam Configuration Schemas
# ============================================


class BeamConfigCreate(BaseModel):
    """Schema for creating beam configuration"""

    beam_color_id: int = Field(..., description="ID of the beam color")
    beam_multiplier: int = Field(
        ..., gt=0, description="Multiplier for beam color (e.g., 2 for B-2)"
    )


class BeamConfigResponse(BaseModel):
    """Schema for beam configuration response"""

    id: int
    order_id: int
    design_number: str
    beam_color_id: int
    beam_color_code: Optional[str] = None
    beam_color_name: Optional[str] = None
    beam_multiplier: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Design Set Tracking Schemas
# ============================================


class DesignSetTrackingResponse(BaseModel):
    """Schema for design set tracking response"""

    id: int
    order_id: int
    design_number: str
    total_sets: int
    allocated_sets: int
    remaining_sets: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Design-Wise Allocation Schemas
# ============================================


class DesignBeamPieces(BaseModel):
    """Beam pieces breakdown for a design"""

    beam_color_code: str
    beam_color_name: str
    beam_multiplier: int
    pieces: int  # calculated: remaining_sets * beam_multiplier


class DesignAllocationDetail(BaseModel):
    """Complete allocation detail for a design"""

    order_id: int
    order_number: Optional[str] = None
    party_name: Optional[str] = None
    quality_name: Optional[str] = None
    design_number: str
    total_sets: int
    allocated_sets: int
    remaining_sets: int
    beam_pieces: List[DesignBeamPieces]


class DesignWiseAllocationResponse(BaseModel):
    """Response for design-wise beam allocation table"""

    designs: List[DesignAllocationDetail]
    total_designs: int
    total_remaining_sets: int


# ============================================
# Complete Beam Summary (All Designs Aggregated)
# ============================================


class BeamColorSummary(BaseModel):
    """Summary for a single beam color across all designs"""

    beam_color_code: str
    beam_color_name: str
    total_pieces: int
    designs_count: int


class QualityBeamSummary(BaseModel):
    """Beam summary grouped by quality"""

    quality_name: str
    beam_colors: List[BeamColorSummary]
    total_pieces: int


class CompleteBeamSummaryResponse(BaseModel):
    """Response for complete beam allocation table (aggregated)"""

    qualities: List[QualityBeamSummary]
    grand_total_pieces: int


# ============================================
# Design Creation Schema (for Order)
# ============================================


class DesignWithBeamsCreate(BaseModel):
    """Schema for creating a design with beam configurations"""

    design_number: str = Field(..., min_length=1, description="Design number/code")
    ground_color_name: str = Field(
        ..., min_length=1, description="Ground color for this design"
    )
    beam_configs: List[BeamConfigCreate] = Field(
        ..., min_items=1, description="Beam color configurations"
    )


# ============================================
# Lot Allocation with Sets Schema
# ============================================


class LotDesignAllocation(BaseModel):
    """Schema for allocating sets to a design in a lot"""

    order_id: int
    design_number: str
    allocated_sets: int = Field(..., gt=0, description="Number of sets to allocate")


class LotCreateFromSets(BaseModel):
    """Schema for creating lot with set-based allocations"""

    party_id: int
    quality_id: int
    lot_date: Optional[str] = None
    lot_number: str = Field(
        ..., min_length=1, description="Manually entered lot number"
    )
    design_allocations: List[LotDesignAllocation] = Field(
        ..., min_items=1, description="Design allocations for this lot"
    )
    bill_number: Optional[str] = None
    actual_pieces: Optional[int] = None
    delivery_date: Optional[str] = None
    notes: Optional[str] = None
