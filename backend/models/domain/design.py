"""
Design domain models for set tracking and beam configuration
"""

from datetime import datetime
from typing import Optional, Union


class DesignSetTracking:
    """Design Set Tracking domain model"""

    def __init__(
        self,
        id: Optional[int] = None,
        order_id: int = 0,
        design_number: str = "",
        total_sets: int = 0,
        allocated_sets: int = 0,
        remaining_sets: int = 0,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.design_number = design_number
        self.total_sets = total_sets
        self.allocated_sets = allocated_sets
        self.remaining_sets = remaining_sets
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "design_number": self.design_number,
            "total_sets": self.total_sets,
            "allocated_sets": self.allocated_sets,
            "remaining_sets": self.remaining_sets,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DesignSetTracking":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id", 0),
            design_number=data.get("design_number", ""),
            total_sets=data.get("total_sets", 0),
            allocated_sets=data.get("allocated_sets", 0),
            remaining_sets=data.get("remaining_sets", 0),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class DesignBeamConfig:
    """Design Beam Configuration domain model"""

    def __init__(
        self,
        id: Optional[int] = None,
        order_id: int = 0,
        design_number: str = "",
        beam_color_id: int = 0,
        beam_multiplier: int = 1,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.design_number = design_number
        self.beam_color_id = beam_color_id
        self.beam_multiplier = beam_multiplier
        self.is_active = is_active
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "design_number": self.design_number,
            "beam_color_id": self.beam_color_id,
            "beam_multiplier": self.beam_multiplier,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DesignBeamConfig":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id", 0),
            design_number=data.get("design_number", ""),
            beam_color_id=data.get("beam_color_id", 0),
            beam_multiplier=data.get("beam_multiplier", 1),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
        )
