"""
Color domain model representing database table structure
"""

from datetime import datetime
from typing import Optional, Union


class Color:
    """Color domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        color_code: str = "",
        color_name: str = "",
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.color_code = color_code
        self.color_name = color_name
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "color_code": self.color_code,
            "color_name": self.color_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Color":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            color_code=data.get("color_code", ""),
            color_name=data.get("color_name", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
