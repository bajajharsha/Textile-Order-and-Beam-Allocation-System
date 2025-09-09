"""
Quality domain model representing database table structure
"""

from datetime import datetime
from typing import Optional, Union


class Quality:
    """Quality domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        quality_name: str = "",
        feeder_count: int = 0,
        specification: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.quality_name = quality_name
        self.feeder_count = feeder_count
        self.specification = specification
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "quality_name": self.quality_name,
            "feeder_count": self.feeder_count,
            "specification": self.specification,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quality":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            quality_name=data.get("quality_name", ""),
            feeder_count=data.get("feeder_count", 0),
            specification=data.get("specification"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
