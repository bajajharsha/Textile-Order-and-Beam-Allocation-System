"""
Master data Pydantic schemas for API validation and serialization
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# Color Schemas
class ColorCreate(BaseModel):
    """Schema for creating colors"""
    color_code: str = Field(..., min_length=1, max_length=10, description="Color code")
    color_name: str = Field(..., min_length=1, max_length=100, description="Color name")

    @field_validator("color_code")
    @classmethod
    def validate_color_code(cls, v):
        """Validate color code"""
        if not v or v.strip() == "":
            raise ValueError("Color code cannot be empty")
        return v.strip().upper()

    @field_validator("color_name")
    @classmethod
    def validate_color_name(cls, v):
        """Validate color name"""
        if not v or v.strip() == "":
            raise ValueError("Color name cannot be empty")
        return v.strip()


class ColorUpdate(BaseModel):
    """Schema for updating colors"""
    color_code: Optional[str] = Field(None, min_length=1, max_length=10)
    color_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

    @field_validator("color_code")
    @classmethod
    def validate_color_code(cls, v):
        """Validate color code"""
        if v is None:
            return v
        if not v or v.strip() == "":
            raise ValueError("Color code cannot be empty")
        return v.strip().upper()

    @field_validator("color_name")
    @classmethod
    def validate_color_name(cls, v):
        """Validate color name"""
        if v is None:
            return v
        if not v or v.strip() == "":
            raise ValueError("Color name cannot be empty")
        return v.strip()


class ColorResponse(BaseModel):
    """Schema for color API responses"""
    id: int
    color_code: str
    color_name: str
    is_active: bool

    class Config:
        from_attributes = True


class ColorListResponse(BaseModel):
    """Schema for color list API responses"""
    colors: List[ColorResponse]
    page: int
    page_size: int
    total: int


# Quality Schemas
class QualityCreate(BaseModel):
    """Schema for creating qualities"""
    quality_name: str = Field(..., min_length=1, max_length=255, description="Quality name")
    feeder_count: int = Field(..., gt=0, description="Number of feeders")
    specification: Optional[str] = Field(None, max_length=255, description="Quality specification")

    @field_validator("quality_name")
    @classmethod
    def validate_quality_name(cls, v):
        """Validate quality name"""
        if not v or v.strip() == "":
            raise ValueError("Quality name cannot be empty")
        return v.strip()

    @field_validator("specification")
    @classmethod
    def validate_specification(cls, v):
        """Validate specification"""
        if v is None:
            return v
        return v.strip() if v.strip() else None


class QualityUpdate(BaseModel):
    """Schema for updating qualities"""
    quality_name: Optional[str] = Field(None, min_length=1, max_length=255)
    feeder_count: Optional[int] = Field(None, gt=0)
    specification: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

    @field_validator("quality_name")
    @classmethod
    def validate_quality_name(cls, v):
        """Validate quality name"""
        if v is None:
            return v
        if not v or v.strip() == "":
            raise ValueError("Quality name cannot be empty")
        return v.strip()

    @field_validator("specification")
    @classmethod
    def validate_specification(cls, v):
        """Validate specification"""
        if v is None:
            return v
        return v.strip() if v.strip() else None


class QualityResponse(BaseModel):
    """Schema for quality API responses"""
    quality_id: int
    quality_name: str
    feeder_count: int
    specification: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class QualityListResponse(BaseModel):
    """Schema for quality list API responses"""
    qualities: List[QualityResponse]
    page: int
    page_size: int
    total: int


# Cut Schemas
class CutCreate(BaseModel):
    """Schema for creating cuts"""
    cut_value: str = Field(..., min_length=1, max_length=20, description="Cut value like 4.10, 6.10")
    description: Optional[str] = Field(None, max_length=100, description="Cut description")

    @field_validator("cut_value")
    @classmethod
    def validate_cut_value(cls, v):
        """Validate cut value"""
        if not v or v.strip() == "":
            raise ValueError("Cut value cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validate description"""
        if v is None:
            return v
        return v.strip() if v.strip() else None


class CutUpdate(BaseModel):
    """Schema for updating cuts"""
    cut_value: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

    @field_validator("cut_value")
    @classmethod
    def validate_cut_value(cls, v):
        """Validate cut value"""
        if v is None:
            return v
        if not v or v.strip() == "":
            raise ValueError("Cut value cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validate description"""
        if v is None:
            return v
        return v.strip() if v.strip() else None


class CutResponse(BaseModel):
    """Schema for cut API responses"""
    id: int
    cut_value: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class CutListResponse(BaseModel):
    """Schema for cut list API responses"""
    cuts: List[CutResponse]
    page: int
    page_size: int
    total: int


# Master Data Search Schemas
class MasterDataSearch(BaseModel):
    """Schema for master data search"""
    search_term: Optional[str] = Field(None, max_length=100, description="Search term")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
