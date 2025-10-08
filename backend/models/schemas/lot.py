"""
Lot schemas for API request/response validation
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class LotAllocationItem(BaseModel):
    """Schema for individual lot allocation item"""

    order_id: int = Field(..., gt=0, description="Order ID")
    design_number: str = Field(..., min_length=1, description="Design number")
    ground_color_name: str = Field(..., min_length=1, description="Ground color name")
    beam_color_id: int = Field(..., gt=0, description="Beam color ID")
    allocated_pieces: int = Field(..., gt=0, description="Number of pieces to allocate")
    notes: Optional[str] = Field(None, max_length=500, description="Allocation notes")

    class Config:
        from_attributes = True


class LotCreate(BaseModel):
    """Schema for creating new lot"""

    party_id: int = Field(..., gt=0, description="Party ID")
    quality_id: int = Field(..., gt=0, description="Quality ID")
    lot_date: Optional[date] = Field(None, description="Lot date (defaults to today)")
    bill_number: Optional[str] = Field(None, max_length=50, description="Bill number")
    actual_pieces: Optional[int] = Field(
        None, gt=0, description="Actual pieces produced"
    )
    delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    notes: Optional[str] = Field(None, max_length=1000, description="Lot notes")
    allocations: List[LotAllocationItem] = Field(
        ..., min_items=1, description="Allocation items"
    )

    @field_validator("allocations")
    @classmethod
    def validate_allocations(cls, v):
        """Validate allocations"""
        if not v:
            raise ValueError("At least one allocation is required")

        # Check for duplicate allocations (same order, design, color)
        seen = set()
        for allocation in v:
            key = (
                allocation.order_id,
                allocation.design_number,
                allocation.ground_color_name,
            )
            if key in seen:
                raise ValueError(
                    f"Duplicate allocation for order {allocation.order_id}, design {allocation.design_number}, color {allocation.ground_color_name}"
                )
            seen.add(key)

        return v

    class Config:
        from_attributes = True


class LotUpdate(BaseModel):
    """Schema for updating lot"""

    bill_number: Optional[str] = Field(None, max_length=50, description="Bill number")
    actual_pieces: Optional[int] = Field(
        None, gt=0, description="Actual pieces produced"
    )
    delivery_date: Optional[date] = Field(None, description="Delivery date")
    status: Optional[str] = Field(None, description="Lot status")
    notes: Optional[str] = Field(None, max_length=1000, description="Lot notes")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status"""
        if v is not None:
            valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "DELIVERED"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    class Config:
        from_attributes = True


class LotAllocationResponse(BaseModel):
    """Schema for lot allocation response"""

    id: int
    lot_id: int
    order_id: int
    design_number: str
    ground_color_name: str
    beam_color_id: int
    allocated_pieces: int
    notes: Optional[str]
    created_at: str

    # Related data
    beam_color_name: Optional[str] = None
    beam_color_code: Optional[str] = None

    class Config:
        from_attributes = True


class LotResponse(BaseModel):
    """Schema for lot response"""

    id: int
    lot_number: str
    lot_date: str
    party_id: int
    quality_id: int
    total_pieces: int
    bill_number: Optional[str]
    actual_pieces: Optional[int]
    delivery_date: Optional[str]
    status: str
    notes: Optional[str]
    created_at: str
    updated_at: str

    # Related data
    party_name: Optional[str] = None
    quality_name: Optional[str] = None
    allocations: List[LotAllocationResponse] = []

    class Config:
        from_attributes = True


class PartywiseDetailItem(BaseModel):
    """Schema for partywise detail (red book) item"""

    date: str  # Order date
    des_no: str  # Design number
    quality: str  # Quality name
    sets_pcs: int  # Remaining pieces
    rate: Decimal  # Rate per piece
    lot_no: Optional[str] = None  # Lot number (if allocated)
    lot_no_date: Optional[str] = None  # Lot date
    bill_no: Optional[str] = None  # Bill number
    actual_pcs: Optional[int] = None  # Actual pieces
    delivery_date: Optional[str] = None  # Delivery date

    # Additional fields
    party_name: str
    order_id: int
    ground_color_name: str
    beam_color_name: Optional[str] = None

    class Config:
        from_attributes = True


class PartywiseDetailResponse(BaseModel):
    """Schema for partywise detail response"""

    party_name: str
    items: List[PartywiseDetailItem]
    total_remaining_pieces: int
    total_allocated_pieces: int
    total_value: Decimal

    class Config:
        from_attributes = True


class LotRegisterItem(BaseModel):
    """Schema for lot register item"""

    lot_date: Optional[str] = None
    lot_no: Optional[str] = None
    party_name: str
    design_no: str
    quality: str
    total_pieces: int  # Sets × Ground Colors (calculated)
    sets: Optional[int] = None  # Original sets value
    ground_colors_count: Optional[int] = None  # Number of ground colors
    bill_no: Optional[str] = None
    actual_pieces: Optional[int] = None
    delivery_date: Optional[str] = None
    status: str

    # Additional fields
    lot_id: Optional[int] = None
    allocation_id: Optional[int] = None
    ground_color_name: Optional[str] = None
    order_id: int
    order_item_id: Optional[int] = None
    party_id: int
    quality_id: int

    class Config:
        from_attributes = True


class LotRegisterResponse(BaseModel):
    """Schema for lot register response"""

    items: List[LotRegisterItem]
    total_lots: int
    total_pieces: int
    total_delivered: int

    class Config:
        from_attributes = True


class OrderItemStatusResponse(BaseModel):
    """Schema for order item status response"""

    id: int
    order_id: int
    design_number: str
    ground_color_name: str
    beam_color_id: int
    total_pieces: int
    allocated_pieces: int
    remaining_pieces: int

    # Related data
    order_number: Optional[str] = None
    party_name: Optional[str] = None
    quality_name: Optional[str] = None
    beam_color_name: Optional[str] = None
    beam_color_code: Optional[str] = None
    rate_per_piece: Optional[Decimal] = None

    class Config:
        from_attributes = True


class BeamSummaryWithAllocation(BaseModel):
    """Schema for beam summary with allocation details"""

    party_name: str
    quality_name: str
    beam_color_code: str
    beam_color_name: str
    total_pieces: int
    allocated_pieces: int
    remaining_pieces: int
    design_count: int

    # Additional calculations
    allocation_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class AllocationSummary(BaseModel):
    """Schema for allocation summary statistics"""

    total_orders: int
    total_pieces: int
    allocated_pieces: int
    remaining_pieces: int
    allocation_percentage: float
    total_lots: int
    pending_lots: int
    completed_lots: int

    class Config:
        from_attributes = True
