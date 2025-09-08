"""
Party Pydantic Schemas - Request/Response validation
"""

from typing import Optional

from pydantic import BaseModel, Field


class PartyCreate(BaseModel):
    """Schema for creating a new party"""

    party_name: str = Field(..., min_length=2, max_length=255, description="Party name")
    contact_number: str = Field(
        ..., min_length=10, max_length=10, description="10-digit contact number"
    )
    broker_name: Optional[str] = Field(None, max_length=255, description="Broker name")
    gst: Optional[str] = Field(None, max_length=15, description="GST number")
    address: Optional[str] = Field(None, max_length=1000, description="Address")


class PartyUpdate(BaseModel):
    """Schema for updating a party"""

    party_name: Optional[str] = Field(None, min_length=2, max_length=255)
    contact_number: Optional[str] = Field(None, min_length=10, max_length=10)
    broker_name: Optional[str] = Field(None, max_length=255)
    gst: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=1000)


class PartyResponse(BaseModel):
    """Schema for party API responses"""

    id: int
    party_name: str
    contact_number: str
    broker_name: Optional[str]
    gst: Optional[str]
    address: Optional[str]
    is_active: bool
    created_at: str  # IST timestamp as string
    updated_at: str  # IST timestamp as string

    class Config:
        from_attributes = True


class PartyListResponse(BaseModel):
    """Schema for party list responses"""

    parties: list[PartyResponse]
    page: int
    page_size: int
    total: int


class PartySearchResponse(BaseModel):
    """Schema for party search responses"""

    parties: list[PartyResponse]
    count: int
