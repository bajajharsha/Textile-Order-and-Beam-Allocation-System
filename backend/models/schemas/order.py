"""
Order Pydantic schemas for API requests and responses
"""

from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class GroundColorItem(BaseModel):
    """Schema for ground color items in order"""

    ground_color_name: str = Field(..., min_length=1, description="Ground color name")
    beam_color_id: int = Field(..., gt=0, description="Beam color ID")

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating orders"""

    party_id: int = Field(..., gt=0, description="Party ID")
    quality_id: int = Field(..., gt=0, description="Quality ID")
    sets: int = Field(..., gt=0, description="Number of sets")
    pick: int = Field(..., gt=0, description="Pick number")
    cuts: List[str] = Field(..., min_items=1, description="List of cut values")
    rate_per_piece: Decimal = Field(
        ..., gt=0, max_digits=10, decimal_places=2, description="Rate per piece"
    )
    design_numbers: List[str] = Field(
        ..., min_items=1, description="List of design numbers"
    )
    ground_colors: List[GroundColorItem] = Field(
        ..., min_items=1, description="Ground colors with beam colors"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    @field_validator("design_numbers")
    @classmethod
    def validate_design_numbers(cls, v):
        """Validate design numbers"""
        if not v:
            raise ValueError("At least one design number is required")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate design numbers are not allowed")

        # Validate each design number
        for design in v:
            if not design or design.strip() == "":
                raise ValueError("Design number cannot be empty")

        return [design.strip().upper() for design in v]

    @field_validator("cuts")
    @classmethod
    def validate_cuts(cls, v):
        """Validate cuts"""
        if not v:
            raise ValueError("At least one cut is required")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate cuts are not allowed")

        return v

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    """Schema for updating orders"""

    party_id: Optional[int] = Field(None, gt=0)
    quality_id: Optional[int] = Field(None, gt=0)
    sets: Optional[int] = Field(None, gt=0)
    pick: Optional[int] = Field(None, gt=0)
    cuts: Optional[List[str]] = Field(None, min_items=1)
    rate_per_piece: Optional[Decimal] = Field(
        None, gt=0, max_digits=10, decimal_places=2
    )
    design_numbers: Optional[List[str]] = Field(None, min_items=1)
    ground_colors: Optional[List[GroundColorItem]] = Field(None, min_items=1)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("design_numbers")
    @classmethod
    def validate_design_numbers(cls, v):
        """Validate design numbers"""
        if v is None:
            return v

        if not v:
            raise ValueError("At least one design number is required")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate design numbers are not allowed")

        # Validate each design number
        for design in v:
            if not design or design.strip() == "":
                raise ValueError("Design number cannot be empty")

        return [design.strip().upper() for design in v]

    @field_validator("cuts")
    @classmethod
    def validate_cuts(cls, v):
        """Validate cuts"""
        if v is None:
            return v

        if not v:
            raise ValueError("At least one cut is required")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate cuts are not allowed")

        return v

    class Config:
        from_attributes = True


class BeamColorSummary(BaseModel):
    """Schema for beam color summary"""

    color_code: str
    color_name: str
    selection_count: int
    calculated_pieces: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order API responses"""

    id: int
    order_number: str
    party_id: int
    quality_id: int
    sets: int
    pick: int
    order_date: str  # Date as string
    rate_per_piece: float
    total_designs: int
    total_pieces: int
    total_value: float
    notes: Optional[str]
    is_active: bool
    created_at: str  # IST timestamp as string
    updated_at: str  # IST timestamp as string

    # Related data
    party_name: Optional[str] = None
    quality_name: Optional[str] = None
    cuts: List[str] = []
    design_numbers: List[str] = []
    ground_colors: List[GroundColorItem] = []
    beam_summary: Dict[str, int] = {}  # {"R": 1, "B": 2}
    beam_colors: List[BeamColorSummary] = []

    class Config:
        from_attributes = True


class OrderListItem(BaseModel):
    """Schema for order list items"""

    id: int
    order_number: str
    order_date: str
    party_name: str
    quality_name: str
    total_designs: int
    total_pieces: int
    total_value: float
    created_at: str

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for order list API responses"""

    orders: List[OrderListItem]
    page: int
    page_size: int
    total: int

    class Config:
        from_attributes = True


class OrderSearchResponse(BaseModel):
    """Schema for order search API responses"""

    orders: List[OrderListItem]
    total: int

    class Config:
        from_attributes = True
