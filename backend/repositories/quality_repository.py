"""
Quality Repository - Database operations
"""

from typing import List, Optional

from config.database import database, get_ist_timestamp
from models.domain.quality import Quality


class QualityRepository:
    """Quality database operations"""

    def __init__(self):
        self.db_client = database

    async def create(self, quality_data: dict) -> Quality:
        """Create new quality"""
        quality_data["created_at"] = get_ist_timestamp()
        quality_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = client.table("qualities").insert(quality_data).execute()
        return Quality.from_dict(result.data[0])

    async def get_by_id(self, quality_id: int) -> Optional[Quality]:
        """Get quality by ID"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .select("*")
            .eq("id", quality_id)
            .eq("is_active", True)
            .execute()
        )
        return Quality.from_dict(result.data[0]) if result.data else None

    async def update(self, quality_id: int, update_data: dict) -> Optional[Quality]:
        """Update quality"""
        update_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = (
            client.table("qualities").update(update_data).eq("id", quality_id).execute()
        )
        return Quality.from_dict(result.data[0]) if result.data else None

    async def delete(self, quality_id: int) -> bool:
        """Soft delete quality"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .update({"is_active": False, "updated_at": get_ist_timestamp()})
            .eq("id", quality_id)
            .execute()
        )
        return bool(result.data)

    async def get_all(self, limit: int = 20, offset: int = 0) -> List[Quality]:
        """Get all active qualities with pagination"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .select("*")
            .eq("is_active", True)
            .order("quality_name", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [Quality.from_dict(quality) for quality in result.data]

    async def count_all(self) -> int:
        """Get total count of active qualities"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return result.count or 0

    async def search(self, query: str, limit: int = 20) -> List[Quality]:
        """Search qualities by name"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .select("*")
            .ilike("quality_name", f"%{query}%")
            .eq("is_active", True)
            .limit(limit)
            .execute()
        )
        return [Quality.from_dict(quality) for quality in result.data]

    async def get_by_name(self, quality_name: str) -> Optional[Quality]:
        """Get quality by name"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .select("*")
            .eq("quality_name", quality_name)
            .eq("is_active", True)
            .execute()
        )
        return Quality.from_dict(result.data[0]) if result.data else None

    async def get_dropdown_list(self) -> List[Quality]:
        """Get qualities for dropdown"""
        client = await self.db_client.get_client()
        result = (
            client.table("qualities")
            .select("id, quality_name, feeder_count")
            .eq("is_active", True)
            .order("quality_name", desc=False)
            .execute()
        )
        return [Quality.from_dict(quality) for quality in result.data]
