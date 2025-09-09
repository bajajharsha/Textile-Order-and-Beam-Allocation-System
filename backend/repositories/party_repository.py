"""
Party Repository - Database operations
"""

from typing import List, Optional

from config.database import database, get_ist_timestamp
from models.domain.party import Party


class PartyRepository:
    """Party database operations"""

    def __init__(self):
        self.db_client = database

    async def create(self, party_data: dict) -> Party:
        """Create new party"""
        # Add IST timestamps
        party_data["created_at"] = get_ist_timestamp()
        party_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = client.table("parties").insert(party_data).execute()
        return Party.from_dict(result.data[0])

    async def get_by_id(self, party_id: int) -> Optional[Party]:
        """Get party by ID"""
        client = await self.db_client.get_client()
        result = (
            client.table("parties")
            .select("*")
            .eq("id", party_id)
            .eq("is_active", True)
            .execute()
        )
        return Party.from_dict(result.data[0]) if result.data else None

    async def update(self, party_id: int, update_data: dict) -> Optional[Party]:
        """Update party"""
        # Add IST timestamp for update
        update_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = (
            client.table("parties").update(update_data).eq("id", party_id).execute()
        )
        return Party.from_dict(result.data[0]) if result.data else None

    async def delete(self, party_id: int) -> bool:
        """Soft delete party"""
        client = await self.db_client.get_client()
        result = (
            client.table("parties")
            .update({"is_active": False, "updated_at": get_ist_timestamp()})
            .eq("id", party_id)
            .execute()
        )
        return bool(result.data)

    async def get_all(self, limit: int = 20, offset: int = 0) -> List[Party]:
        """Get all active parties with pagination"""
        print("party repository get_all")
        client = await self.db_client.get_client()
        result = (
            client.table("parties")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [Party.from_dict(party) for party in result.data]

    async def count_all(self) -> int:
        """Get total count of active parties"""
        client = await self.db_client.get_client()
        result = (
            client.table("parties")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return result.count or 0

    async def search(self, query: str, limit: int = 20) -> List[Party]:
        """Search parties by name"""
        client = await self.db_client.get_client()
        result = (
            client.table("parties")
            .select("*")
            .ilike("party_name", f"%{query}%")
            .eq("is_active", True)
            .limit(limit)
            .execute()
        )
        return [Party.from_dict(party) for party in result.data]

    async def get_by_gst(self, gst: str) -> Optional[Party]:
        """Check if GST already exists"""
        client = await self.db_client.get_client()
        result = (
            client.table("parties")
            .select("*")
            .eq("gst", gst)
            .eq("is_active", True)
            .execute()
        )
        return Party.from_dict(result.data[0]) if result.data else None
