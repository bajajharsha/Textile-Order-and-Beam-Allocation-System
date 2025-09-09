"""
Cut Repository - Database operations
"""

from typing import List, Optional

from config.database import database, get_ist_timestamp
from models.domain.cut import Cut


class CutRepository:
    """Cut database operations"""

    def __init__(self):
        self.db_client = database

    async def create(self, cut_data: dict) -> Cut:
        """Create new cut"""
        cut_data["created_at"] = get_ist_timestamp()
        cut_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = client.table("cuts").insert(cut_data).execute()
        return Cut.from_dict(result.data[0])

    async def get_by_id(self, cut_id: int) -> Optional[Cut]:
        """Get cut by ID"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .select("*")
            .eq("id", cut_id)
            .eq("is_active", True)
            .execute()
        )
        return Cut.from_dict(result.data[0]) if result.data else None

    async def update(self, cut_id: int, update_data: dict) -> Optional[Cut]:
        """Update cut"""
        update_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = client.table("cuts").update(update_data).eq("id", cut_id).execute()
        return Cut.from_dict(result.data[0]) if result.data else None

    async def delete(self, cut_id: int) -> bool:
        """Soft delete cut"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .update({"is_active": False, "updated_at": get_ist_timestamp()})
            .eq("id", cut_id)
            .execute()
        )
        return bool(result.data)

    async def get_all(self, limit: int = 20, offset: int = 0) -> List[Cut]:
        """Get all active cuts with pagination"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .select("*")
            .eq("is_active", True)
            .order("cut_value", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [Cut.from_dict(cut) for cut in result.data]

    async def count_all(self) -> int:
        """Get total count of active cuts"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return result.count or 0

    async def search(self, query: str, limit: int = 20) -> List[Cut]:
        """Search cuts by value or description"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .select("*")
            .or_(f"cut_value.ilike.%{query}%,description.ilike.%{query}%")
            .eq("is_active", True)
            .limit(limit)
            .execute()
        )
        return [Cut.from_dict(cut) for cut in result.data]

    async def get_by_value(self, cut_value: str) -> Optional[Cut]:
        """Get cut by value"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .select("*")
            .eq("cut_value", cut_value)
            .eq("is_active", True)
            .execute()
        )
        return Cut.from_dict(result.data[0]) if result.data else None

    async def get_dropdown_list(self) -> List[Cut]:
        """Get cuts for dropdown"""
        client = await self.db_client.get_client()
        result = (
            client.table("cuts")
            .select("id, cut_value, description")
            .eq("is_active", True)
            .order("cut_value", desc=False)
            .execute()
        )
        return [Cut.from_dict(cut) for cut in result.data]
