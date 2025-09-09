"""
Color Pydantic schemas for API requests and responses
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ColorCreate(BaseModel):
    """Schema for creating colors"""

    color_code: str = Field(
        ..., min_length=1, max_length=10, description="Color code (e.g., R, B, F)"
    )
    color_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Color name (e.g., Red, Black, Firozi)",
    )

    class Config:
        from_attributes = True


class ColorUpdate(BaseModel):
    """Schema for updating colors"""

    color_code: Optional[str] = Field(None, min_length=1, max_length=10)
    color_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class ColorResponse(BaseModel):
    """Schema for color API responses"""

    id: int
    color_code: str
    color_name: str
    is_active: bool
    created_at: str  # IST timestamp as string
    updated_at: str  # IST timestamp as string

    class Config:
        from_attributes = True


class ColorListResponse(BaseModel):
    """Schema for color list API responses"""

    colors: List[ColorResponse]
    page: int
    page_size: int
    total: int

    class Config:
        from_attributes = True


class ColorDropdownResponse(BaseModel):
    """Schema for color dropdown responses"""

    id: int
    color_code: str
    color_name: str

    class Config:
        from_attributes = True
