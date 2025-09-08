"""
Master data service for colors, qualities, and lookup data
Layer 2: Business Logic Layer
"""

from typing import Dict, List

from config.logging import get_logger
from fastapi import HTTPException, status
from models.order import Color, Quality
from repositories.master_repository import MasterDataRepository


class MasterDataService:
    """Service for master data operations"""

    def __init__(self):
        self.master_repo = MasterDataRepository()
        self.logger = get_logger("services.master_data")

    async def get_all_colors(self) -> List[Color]:
        """Get all active colors"""
        try:
            self.logger.debug("Fetching all colors")

            colors = await self.master_repo.color_repo.get_active_colors()
            color_models = [Color(**color) for color in colors]

            self.logger.debug(f"Retrieved {len(color_models)} colors")
            return color_models

        except Exception as e:
            self.logger.error(f"Error fetching colors: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch colors",
            )

    async def get_all_qualities(self) -> List[Quality]:
        """Get all active qualities"""
        try:
            self.logger.debug("Fetching all qualities")

            qualities = await self.master_repo.quality_repo.get_active_qualities()
            quality_models = [Quality(**quality) for quality in qualities]

            self.logger.debug(f"Retrieved {len(quality_models)} qualities")
            return quality_models

        except Exception as e:
            self.logger.error(f"Error fetching qualities: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch qualities",
            )

    async def get_all_master_data(self) -> Dict:
        """Get all master data for forms and dropdowns"""
        try:
            self.logger.debug("Fetching all master data")

            master_data = await self.master_repo.get_all_master_data()

            # Convert to Pydantic models
            colors = [Color(**color) for color in master_data["colors"]]
            qualities = [Quality(**quality) for quality in master_data["qualities"]]

            result = {"colors": colors, "qualities": qualities}

            self.logger.debug(
                f"Retrieved master data: {len(colors)} colors, {len(qualities)} qualities"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error fetching all master data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch master data",
            )

    async def get_color_by_id(self, color_id: int) -> Color:
        """Get color by ID"""
        try:
            self.logger.debug(f"Fetching color with ID: {color_id}")

            color = await self.master_repo.color_repo.get_by_id(color_id)

            if not color:
                self.logger.warning(f"Color not found with ID: {color_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Color not found"
                )

            return Color(**color)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching color by ID {color_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch color",
            )

    async def get_quality_by_id(self, quality_id: int) -> Quality:
        """Get quality by ID"""
        try:
            self.logger.debug(f"Fetching quality with ID: {quality_id}")

            quality = await self.master_repo.quality_repo.get_by_id(quality_id)

            if not quality:
                self.logger.warning(f"Quality not found with ID: {quality_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Quality not found"
                )

            return Quality(**quality)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching quality by ID {quality_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch quality",
            )

    async def initialize_default_data(self) -> bool:
        """Initialize master data with default values"""
        try:
            self.logger.info("Initializing default master data")

            success = await self.master_repo.initialize_master_data()

            if success:
                self.logger.info("Successfully initialized master data")
            else:
                self.logger.warning("Failed to initialize master data")

            return success

        except Exception as e:
            self.logger.error(f"Error initializing master data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize master data",
            )
