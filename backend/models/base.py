"""
Base models and common schemas
Layer 2: Data Models
"""

from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

# Generic type for API responses
T = TypeVar("T")


class BaseEntity(BaseModel):
    """Base entity with common fields"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ActiveMixin(BaseModel):
    """Mixin for active/inactive status"""

    is_active: bool = True


# API Response Models
class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None


class SuccessResponse(APIResponse[T], Generic[T]):
    """Success response wrapper"""

    success: bool = True

    @classmethod
    def create(cls, data: T, message: str = "Operation successful"):
        return cls(data=data, message=message)


class ErrorResponse(APIResponse[None]):
    """Error response wrapper"""

    success: bool = False
    data: None = None

    @classmethod
    def create(cls, message: str, errors: List[str] = None):
        return cls(message=message, errors=errors or [])


# Pagination Models
class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: Optional[str] = Field(
        default="asc", pattern="^(asc|desc)$", description="Sort order"
    )


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    items: List[T]
    meta: PaginationMeta

    @classmethod
    def create(cls, items: List[T], total_items: int, page: int, page_size: int):
        total_pages = (total_items + page_size - 1) // page_size

        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        return cls(items=items, meta=meta)


# Search and Filter Models
class SearchParams(BaseModel):
    """Search parameters"""

    query: Optional[str] = Field(default=None, description="Search query")
    fields: Optional[List[str]] = Field(default=None, description="Fields to search in")


class FilterParams(BaseModel):
    """Filter parameters"""

    filters: Optional[dict] = Field(default=None, description="Filter criteria")
    date_from: Optional[datetime] = Field(default=None, description="Date range start")
    date_to: Optional[datetime] = Field(default=None, description="Date range end")


# Status Enums
class OrderStatus(str, Enum):
    """Order status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class ProductionStatus(str, Enum):
    """Production status enumeration"""

    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class DeliveryStatus(str, Enum):
    """Delivery status enumeration"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Validation Models
class ValidationError(BaseModel):
    """Validation error details"""

    field: str
    message: str
    value: Optional[str] = None


class ValidationResult(BaseModel):
    """Validation result"""

    is_valid: bool
    errors: List[ValidationError] = []

    @classmethod
    def success(cls):
        return cls(is_valid=True)

    @classmethod
    def failure(cls, errors: List[ValidationError]):
        return cls(is_valid=False, errors=errors)


# Health Check Models
class HealthStatus(BaseModel):
    """Health check status"""

    status: str
    timestamp: datetime
    version: str
    environment: str


class DatabaseHealth(BaseModel):
    """Database health status"""

    status: str
    database: str
    connected: bool
    response_time: Optional[float] = None
    error: Optional[str] = None


class SystemHealth(BaseModel):
    """System health status"""

    status: str
    timestamp: datetime
    application: HealthStatus
    database: DatabaseHealth
    uptime: float
