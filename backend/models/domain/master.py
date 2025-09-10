"""
Master data domain models representing database table structure
"""

from typing import Optional, Union
from datetime import datetime


class Color:
    """Color domain model representing database table structure"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        color_code: str = "",
        color_name: str = "",
        is_active: bool = True,
    ):
        self.id = id
        self.color_code = color_code
        self.color_name = color_name
        self.is_active = is_active

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "color_code": self.color_code,
            "color_name": self.color_name,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Color":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            color_code=data.get("color_code", ""),
            color_name=data.get("color_name", ""),
            is_active=data.get("is_active", True),
        )


class Quality:
    """Quality domain model representing database table structure"""
    
    def __init__(
        self,
        quality_id: Optional[int] = None,
        quality_name: str = "",
        feeder_count: int = 0,
        specification: Optional[str] = None,
        is_active: bool = True,
    ):
        self.quality_id = quality_id
        self.quality_name = quality_name
        self.feeder_count = feeder_count
        self.specification = specification
        self.is_active = is_active

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "quality_id": self.quality_id,
            "quality_name": self.quality_name,
            "feeder_count": self.feeder_count,
            "specification": self.specification,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quality":
        """Create from dictionary (database result)"""
        return cls(
            quality_id=data.get("quality_id"),
            quality_name=data.get("quality_name", ""),
            feeder_count=data.get("feeder_count", 0),
            specification=data.get("specification"),
            is_active=data.get("is_active", True),
        )


class Cut:
    """Cut domain model representing database table structure"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        cut_value: str = "",
        description: Optional[str] = None,
        is_active: bool = True,
    ):
        self.id = id
        self.cut_value = cut_value
        self.description = description
        self.is_active = is_active

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "cut_value": self.cut_value,
            "description": self.description,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cut":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            cut_value=data.get("cut_value", ""),
            description=data.get("description"),
            is_active=data.get("is_active", True),
        )
