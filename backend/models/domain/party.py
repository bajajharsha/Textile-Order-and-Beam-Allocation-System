"""
Party Domain Model - Database schema representation
"""

from datetime import datetime
from typing import Optional, Union


class Party:
    """Party domain model representing database table structure"""

    def __init__(
        self,
        id: Optional[int] = None,
        party_name: str = "",
        contact_number: str = "",
        broker_name: Optional[str] = None,
        gst: Optional[str] = None,
        address: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
    ):
        self.id = id
        self.party_name = party_name
        self.contact_number = contact_number
        self.broker_name = broker_name
        self.gst = gst
        self.address = address
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "party_name": self.party_name,
            "contact_number": self.contact_number,
            "broker_name": self.broker_name,
            "gst": self.gst,
            "address": self.address,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Party":
        """Create from dictionary (database result)"""
        # Handle timestamps - keep as strings for IST format
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        return cls(
            id=data.get("id"),
            party_name=data.get("party_name", ""),
            contact_number=data.get("contact_number", ""),
            broker_name=data.get("broker_name"),
            gst=data.get("gst"),
            address=data.get("address"),
            is_active=data.get("is_active", True),
            created_at=created_at,
            updated_at=updated_at,
        )
