"""
Cut Pydantic schemas for API requests and responses
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CutCreate(BaseModel):
    """Schema for creating cuts"""

    cut_value: str = Field(
        ..., min_length=1, max_length=20, description="Cut value (e.g., 4.10, 6.10)"
    )
    description: Optional[str] = Field(
        None, max_length=100, description="Cut description"
    )

    class Config:
        from_attributes = True


class CutUpdate(BaseModel):
    """Schema for updating cuts"""

    cut_value: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class CutResponse(BaseModel):
    """Schema for cut API responses"""

    id: int
    cut_value: str
    description: Optional[str]
    is_active: bool
    created_at: str  # IST timestamp as string
    updated_at: str  # IST timestamp as string

    class Config:
        from_attributes = True


class CutListResponse(BaseModel):
    """Schema for cut list API responses"""

    cuts: List[CutResponse]
    page: int
    page_size: int
    total: int

    class Config:
        from_attributes = True


class CutDropdownResponse(BaseModel):
    """Schema for cut dropdown responses"""

    id: int
    cut_value: str
    description: Optional[str]

    class Config:
        from_attributes = True
