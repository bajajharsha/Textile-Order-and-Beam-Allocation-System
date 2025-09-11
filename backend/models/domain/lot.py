"""
Lot domain models
"""

from datetime import date, datetime
from typing import Optional, Union


class LotRegister:
    """Lot Register domain model"""

    def __init__(
        self,
        id: Optional[int] = None,
        lot_number: Optional[str] = None,
        lot_date: Optional[Union[str, date]] = None,
        party_id: int = 0,
        quality_id: int = 0,
        total_pieces: int = 0,
        bill_number: Optional[str] = None,
        actual_pieces: Optional[int] = None,
        delivery_date: Optional[Union[str, date]] = None,
        notes: Optional[str] = None,
        status: str = "PENDING",
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.lot_number = lot_number
        self.lot_date = lot_date
        self.party_id = party_id
        self.quality_id = quality_id
        self.total_pieces = total_pieces
        self.bill_number = bill_number
        self.actual_pieces = actual_pieces
        self.delivery_date = delivery_date
        self.notes = notes
        self.status = status
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "lot_number": self.lot_number,
            "lot_date": str(self.lot_date) if self.lot_date else None,
            "party_id": self.party_id,
            "quality_id": self.quality_id,
            "total_pieces": self.total_pieces,
            "bill_number": self.bill_number,
            "actual_pieces": self.actual_pieces,
            "delivery_date": str(self.delivery_date) if self.delivery_date else None,
            "notes": self.notes,
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LotRegister":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            lot_number=data.get("lot_number"),
            lot_date=data.get("lot_date"),
            party_id=data.get("party_id", 0),
            quality_id=data.get("quality_id", 0),
            total_pieces=data.get("total_pieces", 0),
            bill_number=data.get("bill_number"),
            actual_pieces=data.get("actual_pieces"),
            delivery_date=data.get("delivery_date"),
            notes=data.get("notes"),
            status=data.get("status", "PENDING"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class LotAllocation:
    """Lot Allocation domain model"""

    def __init__(
        self,
        id: Optional[int] = None,
        lot_id: int = 0,
        order_id: int = 0,
        design_number: str = "",
        ground_color_name: str = "",
        beam_color_id: int = 0,
        allocated_pieces: int = 0,
        notes: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.lot_id = lot_id
        self.order_id = order_id
        self.design_number = design_number
        self.ground_color_name = ground_color_name
        self.beam_color_id = beam_color_id
        self.allocated_pieces = allocated_pieces
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "lot_id": self.lot_id,
            "order_id": self.order_id,
            "design_number": self.design_number,
            "ground_color_name": self.ground_color_name,
            "beam_color_id": self.beam_color_id,
            "allocated_pieces": self.allocated_pieces,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LotAllocation":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            lot_id=data.get("lot_id", 0),
            order_id=data.get("order_id", 0),
            design_number=data.get("design_number", ""),
            ground_color_name=data.get("ground_color_name", ""),
            beam_color_id=data.get("beam_color_id", 0),
            allocated_pieces=data.get("allocated_pieces", 0),
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class OrderItemStatus:
    """Order Item Status domain model"""

    def __init__(
        self,
        id: Optional[int] = None,
        order_id: int = 0,
        design_number: str = "",
        ground_color_name: str = "",
        beam_color_id: int = 0,
        total_pieces: int = 0,
        allocated_pieces: int = 0,
        remaining_pieces: int = 0,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.design_number = design_number
        self.ground_color_name = ground_color_name
        self.beam_color_id = beam_color_id
        self.total_pieces = total_pieces
        self.allocated_pieces = allocated_pieces
        self.remaining_pieces = remaining_pieces
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "design_number": self.design_number,
            "ground_color_name": self.ground_color_name,
            "beam_color_id": self.beam_color_id,
            "total_pieces": self.total_pieces,
            "allocated_pieces": self.allocated_pieces,
            "remaining_pieces": self.remaining_pieces,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItemStatus":
        """Create from dictionary (database result)"""
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id", 0),
            design_number=data.get("design_number", ""),
            ground_color_name=data.get("ground_color_name", ""),
            beam_color_id=data.get("beam_color_id", 0),
            total_pieces=data.get("total_pieces", 0),
            allocated_pieces=data.get("allocated_pieces", 0),
            remaining_pieces=data.get("remaining_pieces", 0),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
