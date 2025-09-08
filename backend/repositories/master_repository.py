"""
Master data repository for colors, qualities, and other lookup data
Layer 3: Data Access Layer
"""

from typing import Dict, List, Optional

from config.logging import get_logger
from repositories.base_repository import BaseRepository


class ColorRepository(BaseRepository):
    """Repository for color master data"""

    def __init__(self):
        super().__init__("colors")
        self.logger = get_logger("repositories.color")

    def _get_search_fields(self) -> List[str]:
        """Return list of fields that can be searched in color repository"""
        return ["color_name", "color_code"]

    def _get_default_order_field(self) -> str:
        """Return default field for ordering color records"""
        return "color_name"

    async def get_active_colors(self) -> List[Dict]:
        """Get all active colors ordered by name"""
        try:
            self.logger.debug("Fetching all active colors")

            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .order("color_name")
                .execute()
            )

            colors = result.data or []
            self.logger.debug(f"Found {len(colors)} active colors")

            return colors

        except Exception as e:
            self.logger.error(f"Error fetching active colors: {str(e)}")
            raise

    async def get_by_code(self, color_code: str) -> Optional[Dict]:
        """Get color by code"""
        try:
            self.logger.debug(f"Fetching color by code: {color_code}")

            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("color_code", color_code.upper())
                .execute()
            )

            if not result.data:
                return None

            return result.data[0]

        except Exception as e:
            self.logger.error(f"Error fetching color by code {color_code}: {str(e)}")
            raise


class QualityRepository(BaseRepository):
    """Repository for quality master data"""

    def __init__(self):
        super().__init__("qualities")
        self.logger = get_logger("repositories.quality")

    def _get_search_fields(self) -> List[str]:
        """Return list of fields that can be searched in quality repository"""
        return ["quality_name", "specification"]

    def _get_default_order_field(self) -> str:
        """Return default field for ordering quality records"""
        return "quality_name"

    async def get_active_qualities(self) -> List[Dict]:
        """Get all active qualities ordered by name"""
        try:
            self.logger.debug("Fetching all active qualities")

            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .order("quality_name")
                .execute()
            )

            qualities = result.data or []
            self.logger.debug(f"Found {len(qualities)} active qualities")

            return qualities

        except Exception as e:
            self.logger.error(f"Error fetching active qualities: {str(e)}")
            raise

    async def get_by_feeder_count(self, feeder_count: int) -> List[Dict]:
        """Get qualities by feeder count"""
        try:
            self.logger.debug(f"Fetching qualities with feeder count: {feeder_count}")

            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("feeder_count", feeder_count)
                .eq("is_active", True)
                .order("quality_name")
                .execute()
            )

            qualities = result.data or []
            self.logger.debug(
                f"Found {len(qualities)} qualities with feeder count {feeder_count}"
            )

            return qualities

        except Exception as e:
            self.logger.error(
                f"Error fetching qualities by feeder count {feeder_count}: {str(e)}"
            )
            raise


class MasterDataRepository:
    """Combined repository for all master data operations"""

    def __init__(self):
        self.color_repo = ColorRepository()
        self.quality_repo = QualityRepository()
        self.logger = get_logger("repositories.master_data")

    async def get_all_master_data(self) -> Dict:
        """Get all master data for dropdowns and forms"""
        try:
            self.logger.debug("Fetching all master data")

            # Get all master data in parallel
            colors = await self.color_repo.get_active_colors()
            qualities = await self.quality_repo.get_active_qualities()

            master_data = {
                "colors": colors,
                "qualities": qualities,
            }

            self.logger.debug(
                f"Retrieved master data: {len(colors)} colors, {len(qualities)} qualities"
            )

            return master_data

        except Exception as e:
            self.logger.error(f"Error fetching all master data: {str(e)}")
            raise

    async def initialize_master_data(self) -> bool:
        """Initialize master data with default values if tables are empty"""
        try:
            self.logger.info("Initializing master data")

            # Check if colors exist
            colors = await self.color_repo.get_active_colors()
            if not colors:
                self.logger.info("Initializing default colors")

                default_colors = [
                    {"color_code": "R", "color_name": "Red", "is_active": True},
                    {"color_code": "F", "color_name": "Firozi", "is_active": True},
                    {"color_code": "B", "color_name": "Black", "is_active": True},
                    {"color_code": "G", "color_name": "Gold", "is_active": True},
                    {"color_code": "RB", "color_name": "Royal Blue", "is_active": True},
                    {"color_code": "W", "color_name": "White", "is_active": True},
                ]

                for color_data in default_colors:
                    await self.color_repo.create(color_data)

                self.logger.info(f"Created {len(default_colors)} default colors")

            # Check if qualities exist
            qualities = await self.quality_repo.get_active_qualities()
            if not qualities:
                self.logger.info("Initializing default qualities")

                default_qualities = [
                    {
                        "quality_name": "2 feeder 50/600",
                        "feeder_count": 2,
                        "specification": "50/600",
                        "is_active": True,
                    },
                    {
                        "quality_name": "3 feeder 40/500",
                        "feeder_count": 3,
                        "specification": "40/500",
                        "is_active": True,
                    },
                    {
                        "quality_name": "4 feeder 60/700",
                        "feeder_count": 4,
                        "specification": "60/700",
                        "is_active": True,
                    },
                ]

                for quality_data in default_qualities:
                    await self.quality_repo.create(quality_data)

                self.logger.info(f"Created {len(default_qualities)} default qualities")

            self.logger.info("Master data initialization completed")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing master data: {str(e)}")
            raise
