"""
Party Use Cases - Business Logic
"""

from typing import List

from fastapi import Depends
from models.domain.party import Party
from repositories.party_repository import PartyRepository
from utils.validation_utils import validate_party_data


class PartyUseCase:
    """Party business logic"""

    def __init__(self, party_repository: PartyRepository = Depends()):
        self.repository = party_repository

    async def create_party(self, party_data: dict) -> Party:
        """Create new party with validation"""
        # Validate data
        validated_data = validate_party_data(party_data)

        # Check if GST already exists
        if validated_data.get("gst"):
            existing_party = await self.repository.get_by_gst(validated_data["gst"])
            if existing_party:
                raise ValueError("Party with this GST already exists")

        # Create party
        return await self.repository.create(validated_data)

    async def get_party(self, party_id: int) -> Party:
        """Get party by ID"""
        party = await self.repository.get_by_id(party_id)
        if not party:
            raise ValueError("Party not found")
        return party

    async def update_party(self, party_id: int, update_data: dict) -> Party:
        """Update party with validation"""
        # Check if party exists
        existing_party = await self.repository.get_by_id(party_id)
        if not existing_party:
            raise ValueError("Party not found")

        # Validate update data
        validated_data = validate_party_data(update_data, is_update=True)

        # Check GST uniqueness if being updated
        if validated_data.get("gst") and validated_data["gst"] != existing_party.get(
            "gst"
        ):
            gst_party = await self.repository.get_by_gst(validated_data["gst"])
            if gst_party:
                raise ValueError("Another party with this GST already exists")

        return await self.repository.update(party_id, validated_data)

    async def delete_party(self, party_id: int) -> bool:
        """Delete party"""
        party = await self.repository.get_by_id(party_id)
        if not party:
            raise ValueError("Party not found")

        return await self.repository.delete(party_id)

    async def list_parties(self, page: int = 1, page_size: int = 20) -> dict:
        """List parties with pagination"""
        print(f"Listing parties with page: {page} and page_size: {page_size}")
        offset = (page - 1) * page_size
        parties = await self.repository.get_all(limit=page_size, offset=offset)
        total_count = await self.repository.count_all()

        return {
            "parties": parties,
            "page": page,
            "page_size": page_size,
            "total": total_count,
        }

    async def search_parties(self, query: str, limit: int = 20) -> List[Party]:
        """Search parties"""
        if not query or len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return await self.repository.search(query, limit)
