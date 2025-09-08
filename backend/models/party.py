"""
Party (Customer) models and schemas
Layer 2: Data Models
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from models.base import ActiveMixin, BaseEntity


# Base Party Model
class PartyBase(BaseModel):
    """Base party model with common fields"""

    party_name: str = Field(
        ..., min_length=2, max_length=255, description="Name of the party/customer"
    )
    contact_number: str = Field(
        ..., min_length=10, max_length=20, description="Contact phone number"
    )
    broker_name: Optional[str] = Field(
        None, max_length=255, description="Broker name if applicable"
    )
    gst: Optional[str] = Field(
        None, max_length=20, description="GST number in Indian format"
    )
    address: Optional[str] = Field(
        None, max_length=1000, description="Complete address"
    )

    @field_validator("party_name")
    @classmethod
    def validate_party_name(cls, v):
        """Validate party name"""
        if not v or v.strip() == "":
            raise ValueError("Party name cannot be empty")

        # Remove extra spaces
        v = " ".join(v.split())

        if len(v) < 2:
            raise ValueError("Party name must be at least 2 characters long")

        return v.title()  # Capitalize each word

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v):
        """Validate contact number format"""
        if not v:
            raise ValueError("Contact number is required")

        # Remove all non-digit characters except +
        cleaned_number = re.sub(r"[^\d+]", "", v)

        # Indian mobile number validation
        if cleaned_number.startswith("+91"):
            cleaned_number = cleaned_number[3:]
        elif cleaned_number.startswith("91") and len(cleaned_number) == 12:
            cleaned_number = cleaned_number[2:]
        elif cleaned_number.startswith("0"):
            cleaned_number = cleaned_number[1:]

        # Check if it's a valid 10-digit Indian mobile number
        if not re.match(r"^[6-9]\d{9}$", cleaned_number):
            raise ValueError("Invalid Indian mobile number format")

        return f"+91{cleaned_number}"

    @field_validator("gst")
    @classmethod
    def validate_gst(cls, v):
        """Validate GST number format"""
        if not v:
            return None

        # Remove spaces and convert to uppercase
        gst_clean = v.replace(" ", "").upper()

        # GST format: 22AAAAA0000A1Z5 (15 characters)
        gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

        if not re.match(gst_pattern, gst_clean):
            raise ValueError("Invalid GST format. Expected format: 22AAAAA0000A1Z5")

        return gst_clean

    @field_validator("broker_name")
    @classmethod
    def validate_broker_name(cls, v):
        """Validate broker name"""
        if not v:
            return None

        v = v.strip()
        if v == "":
            return None

        return v.title()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        """Validate address"""
        if not v:
            return None

        v = v.strip()
        if v == "":
            return None

        return v


# Party Creation Model
class PartyCreate(PartyBase):
    """Model for creating new party"""

    pass


# Party Update Model
class PartyUpdate(BaseModel):
    """Model for updating existing party"""

    party_name: Optional[str] = Field(None, min_length=2, max_length=255)
    contact_number: Optional[str] = Field(None, min_length=10, max_length=20)
    broker_name: Optional[str] = Field(None, max_length=255)
    gst: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None

    # Use the same validators as PartyBase
    @field_validator("party_name")
    @classmethod
    def validate_party_name(cls, v):
        """Validate party name"""
        if v is None:
            return v
        if not v or v.strip() == "":
            raise ValueError("Party name cannot be empty")
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Party name must be at least 2 characters long")
        return v.title()

    @field_validator("gst")
    @classmethod
    def validate_gst(cls, v):
        """Validate GST number format"""
        if not v:
            return None
        gst_clean = v.replace(" ", "").upper()
        gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z][Z][0-9A-Z]$"
        if not re.match(gst_pattern, gst_clean):
            raise ValueError("Invalid GST format. Expected format: 22AAAAA0000A1Z5")
        return gst_clean


# Party Response Model
class PartyResponse(PartyBase, BaseEntity, ActiveMixin):
    """Model for party API responses"""

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# Party List Item Model (for list views)
class PartyListItem(BaseModel):
    """Simplified party model for list views"""

    id: int
    party_name: str
    contact_number: str
    broker_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Party Search Model
class PartySearch(BaseModel):
    """Model for party search parameters"""

    search_term: Optional[str] = Field(
        None, max_length=100, description="Search term for party name or broker name"
    )
    include_inactive: bool = Field(
        default=False, description="Include inactive parties in search"
    )
    has_gst: Optional[bool] = Field(None, description="Filter by GST availability")
    has_broker: Optional[bool] = Field(
        None, description="Filter by broker availability"
    )


# Party Statistics Model
class PartyStats(BaseModel):
    """Party statistics for dashboard"""

    total_parties: int
    active_parties: int
    inactive_parties: int
    parties_with_gst: int
    parties_with_broker: int
    recent_parties: List[PartyListItem] = []


# Party Validation Model
class PartyValidation(BaseModel):
    """Party data validation model"""

    party_name_exists: bool = False
    gst_exists: bool = False
    contact_number_exists: bool = False
    is_valid: bool = True
    errors: List[str] = []
