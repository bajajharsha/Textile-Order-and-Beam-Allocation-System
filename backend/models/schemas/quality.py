"""
Quality Pydantic schemas for API requests and responses
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class QualityCreate(BaseModel):
    """Schema for creating qualities"""

    quality_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Quality name (e.g., 2 feeder 50/600)",
    )
    feeder_count: int = Field(..., gt=0, description="Number of feeders")
    specification: Optional[str] = Field(
        None, max_length=255, description="Additional specifications"
    )

    class Config:
        from_attributes = True


class QualityUpdate(BaseModel):
    """Schema for updating qualities"""

    quality_name: Optional[str] = Field(None, min_length=1, max_length=255)
    feeder_count: Optional[int] = Field(None, gt=0)
    specification: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class QualityResponse(BaseModel):
    """Schema for quality API responses"""

    id: int
    quality_name: str
    feeder_count: int
    specification: Optional[str]
    is_active: bool
    created_at: str  # IST timestamp as string
    updated_at: str  # IST timestamp as string

    class Config:
        from_attributes = True


class QualityListResponse(BaseModel):
    """Schema for quality list API responses"""

    qualities: List[QualityResponse]
    page: int
    page_size: int
    total: int

    class Config:
        from_attributes = True


class QualityDropdownResponse(BaseModel):
    """Schema for quality dropdown responses"""

    id: int
    quality_name: str
    feeder_count: int

    class Config:
        from_attributes = True
