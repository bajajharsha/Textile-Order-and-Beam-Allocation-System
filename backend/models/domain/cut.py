"""
Cut domain model representing database table structure
"""

from datetime import datetime
from typing import Optional, Union


class Cut:
    """Cut domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        cut_value: str = "",
        description: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.cut_value = cut_value
        self.description = description
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "cut_value": self.cut_value,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cut":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            cut_value=data.get("cut_value", ""),
            description=data.get("description"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
