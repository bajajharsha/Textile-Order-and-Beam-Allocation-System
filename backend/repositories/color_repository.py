"""
Color Repository - Database operations
"""

from typing import List, Optional

from config.database import database, get_ist_timestamp
from models.domain.color import Color


class ColorRepository:
    """Color database operations"""

    def __init__(self):
        self.db_client = database

    async def create(self, color_data: dict) -> Color:
        """Create new color"""
        color_data["created_at"] = get_ist_timestamp()
        color_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = client.table("colors").insert(color_data).execute()
        return Color.from_dict(result.data[0])

    async def get_by_id(self, color_id: int) -> Optional[Color]:
        """Get color by ID"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .select("*")
            .eq("id", color_id)
            .eq("is_active", True)
            .execute()
        )
        return Color.from_dict(result.data[0]) if result.data else None

    async def update(self, color_id: int, update_data: dict) -> Optional[Color]:
        """Update color"""
        update_data["updated_at"] = get_ist_timestamp()

        client = await self.db_client.get_client()
        result = client.table("colors").update(update_data).eq("id", color_id).execute()
        return Color.from_dict(result.data[0]) if result.data else None

    async def delete(self, color_id: int) -> bool:
        """Soft delete color"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .update({"is_active": False, "updated_at": get_ist_timestamp()})
            .eq("id", color_id)
            .execute()
        )
        return bool(result.data)

    async def get_all(self, limit: int = 20, offset: int = 0) -> List[Color]:
        """Get all active colors with pagination"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .select("*")
            .eq("is_active", True)
            .order("color_name", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [Color.from_dict(color) for color in result.data]

    async def count_all(self) -> int:
        """Get total count of active colors"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        return result.count or 0

    async def search(self, query: str, limit: int = 20) -> List[Color]:
        """Search colors by name or code"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .select("*")
            .or_(f"color_name.ilike.%{query}%,color_code.ilike.%{query}%")
            .eq("is_active", True)
            .limit(limit)
            .execute()
        )
        return [Color.from_dict(color) for color in result.data]

    async def get_by_code(self, color_code: str) -> Optional[Color]:
        """Get color by code"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .select("*")
            .eq("color_code", color_code)
            .eq("is_active", True)
            .execute()
        )
        return Color.from_dict(result.data[0]) if result.data else None

    async def get_dropdown_list(self) -> List[Color]:
        """Get colors for dropdown"""
        client = await self.db_client.get_client()
        result = (
            client.table("colors")
            .select("id, color_code, color_name")
            .eq("is_active", True)
            .order("color_name", desc=False)
            .execute()
        )
        return [Color.from_dict(color) for color in result.data]
