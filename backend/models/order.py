"""
Order models and schemas
Layer 2: Data Models
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from models.base import BaseEntity, OrderStatus


# Master Data Models
class Color(BaseModel):
    """Color master model"""

    id: int
    color_code: str
    color_name: str
    is_active: bool = True

    class Config:
        from_attributes = True


class Quality(BaseModel):
    """Quality master model"""

    id: int
    quality_name: str
    feeder_count: int
    specification: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# Order Item Models
class OrderItemBase(BaseModel):
    """Base order item model"""

    design_number: str = Field(
        ..., min_length=1, max_length=50, description="Design number/identifier"
    )
    ground_color_id: int = Field(
        ..., gt=0, description="Ground color ID from colors master"
    )
    beam_color_id: int = Field(
        ..., gt=0, description="Beam color ID from colors master"
    )
    pieces_per_color: int = Field(..., gt=0, description="Number of pieces per color")
    designs_per_beam: int = Field(
        default=1, gt=0, description="Number of designs per beam"
    )

    @field_validator("design_number")
    @classmethod
    def validate_design_number(cls, v):
        """Validate design number format"""
        if not v or v.strip() == "":
            raise ValueError("Design number cannot be empty")

        v = v.strip().upper()

        # Allow alphanumeric characters, hyphens, underscores, and spaces
        import re

        if not re.match(r"^[A-Z0-9\-_\s]+$", v):
            raise ValueError(
                "Design number can only contain letters, numbers, hyphens, underscores, and spaces"
            )

        return v


class OrderItemCreate(OrderItemBase):
    """Model for creating order items"""

    pass


class OrderItemResponse(OrderItemBase):
    """Model for order item responses"""

    id: int
    order_id: int
    calculated_pieces: int = Field(
        description="Calculated pieces: pieces_per_color × designs_per_beam × total_designs"
    )
    created_at: datetime

    # Related data
    ground_color: Optional[Color] = None
    beam_color: Optional[Color] = None

    class Config:
        from_attributes = True


# Order Models
class OrderBase(BaseModel):
    """Base order model"""

    party_id: int = Field(..., gt=0, description="Party ID from parties master")
    quality_id: int = Field(..., gt=0, description="Quality ID from qualities master")
    rate_per_piece: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Rate per piece in currency",
    )
    notes: Optional[str] = Field(
        None, max_length=1000, description="Additional notes for the order"
    )

    @field_validator("rate_per_piece")
    @classmethod
    def validate_rate(cls, v):
        """Validate rate per piece"""
        if v <= 0:
            raise ValueError("Rate per piece must be positive")

        if v > 10000:  # Reasonable upper limit
            raise ValueError("Rate per piece seems too high")

        return round(v, 2)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        """Validate notes"""
        if not v:
            return None

        v = v.strip()
        if v == "":
            return None

        return v


class OrderCreate(OrderBase):
    """Model for creating new orders"""

    order_items: List[OrderItemCreate] = Field(
        ..., min_items=1, description="List of order items (design/color combinations)"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_order_items(cls, values):
        """Validate order items"""
        order_items = values.get("order_items", [])

        if not order_items:
            raise ValueError("Order must have at least one item")

        # Check for duplicate design numbers
        design_numbers = [item.design_number for item in order_items]
        if len(design_numbers) != len(set(design_numbers)):
            raise ValueError("Duplicate design numbers are not allowed")

        return values


class OrderUpdate(BaseModel):
    """Model for updating existing orders"""

    party_id: Optional[int] = Field(None, gt=0)
    quality_id: Optional[int] = Field(None, gt=0)
    rate_per_piece: Optional[Decimal] = Field(
        None, gt=0, max_digits=10, decimal_places=2
    )
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[OrderStatus] = None

    # Use the same validators as OrderBase
    @field_validator("rate_per_piece")
    @classmethod
    def validate_rate(cls, v):
        """Validate rate per piece"""
        if v is None:
            return v
        if v <= 0:
            raise ValueError("Rate per piece must be positive")
        if v > 10000:
            raise ValueError("Rate per piece seems too high")
        return round(v, 2)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v):
        """Validate notes"""
        if not v:
            return None
        v = v.strip()
        if v == "":
            return None
        return v


class OrderResponse(OrderBase, BaseEntity):
    """Model for order API responses"""

    order_number: str = Field(description="Unique order number")
    order_date: date = Field(description="Order date")
    total_designs: int = Field(description="Total number of unique designs")
    status: OrderStatus = OrderStatus.PENDING

    # Order items
    order_items: List[OrderItemResponse] = []

    # Calculated fields
    total_pieces: int = Field(default=0, description="Total calculated pieces")
    total_value: Decimal = Field(default=0, description="Total order value")

    # Related data
    party_name: Optional[str] = None
    quality_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }


# Order List Models
class OrderListItem(BaseModel):
    """Simplified order model for list views"""

    id: int
    order_number: str
    order_date: date
    party_name: str
    quality_name: str
    total_pieces: int
    total_value: Decimal
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }


# Order Search and Filter Models
class OrderSearch(BaseModel):
    """Model for order search parameters"""

    search_term: Optional[str] = Field(
        None,
        max_length=100,
        description="Search in order number, party name, or design numbers",
    )
    party_id: Optional[int] = Field(None, gt=0, description="Filter by specific party")
    quality_id: Optional[int] = Field(
        None, gt=0, description="Filter by specific quality"
    )
    status: Optional[OrderStatus] = Field(None, description="Filter by order status")
    date_from: Optional[date] = Field(None, description="Filter orders from this date")
    date_to: Optional[date] = Field(None, description="Filter orders until this date")

    @model_validator(mode="after")
    def validate_date_range(self):
        """Validate date range"""
        if self.date_to and self.date_from and self.date_to < self.date_from:
            raise ValueError("End date must be after start date")
        return self


# Beam Summary Models
class BeamColorSummary(BaseModel):
    """Beam color summary for quality-wise reports"""

    color_id: int
    color_name: str
    color_code: str
    total_pieces: int
    orders_count: int


class QualitySummary(BaseModel):
    """Quality-wise beam summary"""

    quality_id: int
    quality_name: str
    beam_colors: List[BeamColorSummary]
    total_pieces: int
    total_orders: int


class BeamSummaryReport(BaseModel):
    """Complete beam summary report"""

    report_date: datetime
    qualities: List[QualitySummary]
    grand_total_pieces: int
    grand_total_orders: int


# Order Statistics Model
class OrderStats(BaseModel):
    """Order statistics for dashboard"""

    total_orders: int
    pending_orders: int
    completed_orders: int
    total_value: Decimal
    recent_orders: List[OrderListItem] = []
    top_parties: List[dict] = []  # {party_name, order_count, total_value}


# Order Calculation Models
class OrderCalculation(BaseModel):
    """Order calculation result"""

    total_designs: int
    total_pieces: int
    total_value: Decimal
    item_calculations: List[dict] = []  # Individual item calculations


class BeamCalculation(BaseModel):
    """Beam calculation for individual item"""

    design_number: str
    ground_color_name: str
    beam_color_name: str
    pieces_per_color: int
    designs_per_beam: int
    total_designs: int
    calculated_pieces: int
    formula: str = Field(default="pieces_per_color × designs_per_beam × total_designs")
