"""
Master Data Use Cases - Business Logic for Color, Quality, Cut
"""

from typing import Any, Dict, List

from models.domain.color import Color
from models.domain.cut import Cut
from models.domain.quality import Quality
from repositories.color_repository import ColorRepository
from repositories.cut_repository import CutRepository
from repositories.party_repository import PartyRepository
from repositories.quality_repository import QualityRepository


class MasterUseCase:
    """Master data business logic"""

    def __init__(self):
        self.color_repository = ColorRepository()
        self.quality_repository = QualityRepository()
        self.cut_repository = CutRepository()
        self.party_repository = PartyRepository()

    # Color operations
    async def create_color(self, color_data: dict) -> Color:
        """Create new color with validation"""
        # Check if color code already exists
        existing_color = await self.color_repository.get_by_code(
            color_data["color_code"]
        )
        if existing_color:
            raise ValueError(f"Color code '{color_data['color_code']}' already exists")

        return await self.color_repository.create(color_data)

    async def get_color(self, color_id: int) -> Color:
        """Get color by ID"""
        color = await self.color_repository.get_by_id(color_id)
        if not color:
            raise ValueError("Color not found")
        return color

    async def update_color(self, color_id: int, update_data: dict) -> Color:
        """Update color"""
        color = await self.color_repository.get_by_id(color_id)
        if not color:
            raise ValueError("Color not found")

        # Check if color code already exists (for different color)
        if "color_code" in update_data:
            existing_color = await self.color_repository.get_by_code(
                update_data["color_code"]
            )
            if existing_color and existing_color.id != color_id:
                raise ValueError(
                    f"Color code '{update_data['color_code']}' already exists"
                )

        return await self.color_repository.update(color_id, update_data)

    async def delete_color(self, color_id: int) -> bool:
        """Delete color"""
        color = await self.color_repository.get_by_id(color_id)
        if not color:
            raise ValueError("Color not found")

        return await self.color_repository.delete(color_id)

    async def list_colors(self, page: int = 1, page_size: int = 20) -> dict:
        """List colors with pagination"""
        offset = (page - 1) * page_size
        colors = await self.color_repository.get_all(limit=page_size, offset=offset)
        total_count = await self.color_repository.count_all()

        return {
            "colors": colors,
            "page": page,
            "page_size": page_size,
            "total": total_count,
        }

    async def search_colors(self, query: str, limit: int = 20) -> List[Color]:
        """Search colors"""
        return await self.color_repository.search(query, limit)

    async def get_colors_dropdown(self) -> List[Color]:
        """Get colors for dropdown"""
        return await self.color_repository.get_dropdown_list()

    # Quality operations
    async def create_quality(self, quality_data: dict) -> Quality:
        """Create new quality with validation"""
        # Check if quality name already exists
        existing_quality = await self.quality_repository.get_by_name(
            quality_data["quality_name"]
        )
        if existing_quality:
            raise ValueError(f"Quality '{quality_data['quality_name']}' already exists")

        return await self.quality_repository.create(quality_data)

    async def get_quality(self, quality_id: int) -> Quality:
        """Get quality by ID"""
        quality = await self.quality_repository.get_by_id(quality_id)
        if not quality:
            raise ValueError("Quality not found")
        return quality

    async def update_quality(self, quality_id: int, update_data: dict) -> Quality:
        """Update quality"""
        quality = await self.quality_repository.get_by_id(quality_id)
        if not quality:
            raise ValueError("Quality not found")

        # Check if quality name already exists (for different quality)
        if "quality_name" in update_data:
            existing_quality = await self.quality_repository.get_by_name(
                update_data["quality_name"]
            )
            if existing_quality and existing_quality.id != quality_id:
                raise ValueError(
                    f"Quality '{update_data['quality_name']}' already exists"
                )

        return await self.quality_repository.update(quality_id, update_data)

    async def delete_quality(self, quality_id: int) -> bool:
        """Delete quality"""
        quality = await self.quality_repository.get_by_id(quality_id)
        if not quality:
            raise ValueError("Quality not found")

        return await self.quality_repository.delete(quality_id)

    async def list_qualities(self, page: int = 1, page_size: int = 20) -> dict:
        """List qualities with pagination"""
        offset = (page - 1) * page_size
        qualities = await self.quality_repository.get_all(
            limit=page_size, offset=offset
        )
        total_count = await self.quality_repository.count_all()

        return {
            "qualities": qualities,
            "page": page,
            "page_size": page_size,
            "total": total_count,
        }

    async def search_qualities(self, query: str, limit: int = 20) -> List[Quality]:
        """Search qualities"""
        return await self.quality_repository.search(query, limit)

    async def get_qualities_dropdown(self) -> List[Quality]:
        """Get qualities for dropdown"""
        return await self.quality_repository.get_dropdown_list()

    # Cut operations
    async def create_cut(self, cut_data: dict) -> Cut:
        """Create new cut with validation"""
        # Check if cut value already exists
        existing_cut = await self.cut_repository.get_by_value(cut_data["cut_value"])
        if existing_cut:
            raise ValueError(f"Cut '{cut_data['cut_value']}' already exists")

        return await self.cut_repository.create(cut_data)

    async def get_cut(self, cut_id: int) -> Cut:
        """Get cut by ID"""
        cut = await self.cut_repository.get_by_id(cut_id)
        if not cut:
            raise ValueError("Cut not found")
        return cut

    async def update_cut(self, cut_id: int, update_data: dict) -> Cut:
        """Update cut"""
        cut = await self.cut_repository.get_by_id(cut_id)
        if not cut:
            raise ValueError("Cut not found")

        # Check if cut value already exists (for different cut)
        if "cut_value" in update_data:
            existing_cut = await self.cut_repository.get_by_value(
                update_data["cut_value"]
            )
            if existing_cut and existing_cut.id != cut_id:
                raise ValueError(f"Cut '{update_data['cut_value']}' already exists")

        return await self.cut_repository.update(cut_id, update_data)

    async def delete_cut(self, cut_id: int) -> bool:
        """Delete cut"""
        cut = await self.cut_repository.get_by_id(cut_id)
        if not cut:
            raise ValueError("Cut not found")

        return await self.cut_repository.delete(cut_id)

    async def list_cuts(self, page: int = 1, page_size: int = 20) -> dict:
        """List cuts with pagination"""
        offset = (page - 1) * page_size
        cuts = await self.cut_repository.get_all(limit=page_size, offset=offset)
        total_count = await self.cut_repository.count_all()

        return {
            "cuts": cuts,
            "page": page,
            "page_size": page_size,
            "total": total_count,
        }

    async def search_cuts(self, query: str, limit: int = 20) -> List[Cut]:
        """Search cuts"""
        return await self.cut_repository.search(query, limit)

    async def get_cuts_dropdown(self) -> List[Cut]:
        """Get cuts for dropdown"""
        return await self.cut_repository.get_dropdown_list()

    # Combined dropdown data for order form
    async def get_dropdown_data(self) -> Dict[str, Any]:
        """Get all dropdown data for order form"""
        colors = await self.get_colors_dropdown()
        qualities = await self.get_qualities_dropdown()
        cuts = await self.get_cuts_dropdown()

        # Get parties for dropdown (active parties only)
        parties = await self.party_repository.get_dropdown_list()

        return {
            "parties": [
                {"id": party.id, "name": party.party_name} for party in parties
            ],
            "colors": [color.to_dict() for color in colors],
            "qualities": [quality.to_dict() for quality in qualities],
            "cuts": [cut.to_dict() for cut in cuts],
        }
