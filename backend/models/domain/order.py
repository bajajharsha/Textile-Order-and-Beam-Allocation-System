"""
Order domain models representing database table structures
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union


class Order:
    """Order domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        order_number: str = "",
        party_id: int = 0,
        quality_id: int = 0,
        sets: int = 0,
        pick: int = 0,
        order_date: Optional[Union[str, date]] = None,
        rate_per_piece: Union[Decimal, float] = 0.0,
        total_designs: int = 0,
        total_pieces: int = 0,
        total_value: Union[Decimal, float] = 0.0,
        notes: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.order_number = order_number
        self.party_id = party_id
        self.quality_id = quality_id
        self.sets = sets
        self.pick = pick
        self.order_date = order_date
        self.rate_per_piece = (
            Decimal(str(rate_per_piece)) if rate_per_piece else Decimal("0.0")
        )
        self.total_designs = total_designs
        self.total_pieces = total_pieces
        self.total_value = Decimal(str(total_value)) if total_value else Decimal("0.0")
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "party_id": self.party_id,
            "quality_id": self.quality_id,
            "sets": self.sets,
            "pick": self.pick,
            "order_date": self.order_date,
            "rate_per_piece": float(self.rate_per_piece),
            "total_designs": self.total_designs,
            "total_pieces": self.total_pieces,
            "total_value": float(self.total_value),
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            order_number=data.get("order_number", ""),
            party_id=data.get("party_id", 0),
            quality_id=data.get("quality_id", 0),
            sets=data.get("sets", 0),
            pick=data.get("pick", 0),
            order_date=data.get("order_date"),
            rate_per_piece=data.get("rate_per_piece", 0.0),
            total_designs=data.get("total_designs", 0),
            total_pieces=data.get("total_pieces", 0),
            total_value=data.get("total_value", 0.0),
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class OrderCut:
    """Order Cut domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        order_id: int = 0,
        cut_value: str = "",
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.cut_value = cut_value
        self.is_active = is_active
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "cut_value": self.cut_value,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderCut":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id", 0),
            cut_value=data.get("cut_value", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
        )


class OrderItem:
    """Order Item domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        order_id: int = 0,
        design_number: str = "",
        ground_color_name: str = "",
        beam_color_id: int = 0,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.design_number = design_number
        self.ground_color_name = ground_color_name
        self.beam_color_id = beam_color_id
        self.is_active = is_active
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "design_number": self.design_number,
            "ground_color_name": self.ground_color_name,
            "beam_color_id": self.beam_color_id,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id", 0),
            design_number=data.get("design_number", ""),
            ground_color_name=data.get("ground_color_name", ""),
            beam_color_id=data.get("beam_color_id", 0),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
        )
