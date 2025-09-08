"""
Master data controller for API request handling
Layer 1: Presentation Layer
"""

from typing import Dict, List

from config.logging import get_logger
from fastapi import Depends, HTTPException
from models.base import APIResponse, SuccessResponse
from models.order import Color, Quality
from services.master_service import MasterDataService


class MasterDataController:
    """Controller for master data API endpoints"""

    def __init__(self):
        self.logger = get_logger("controllers.master_data")

    def get_master_service(self) -> MasterDataService:
        """Dependency to get master data service instance"""
        return MasterDataService()

    async def get_all_colors(
        self, master_service: MasterDataService = Depends(get_master_service)
    ) -> APIResponse[List[Color]]:
        """Get all active colors"""
        try:
            self.logger.debug("Getting all colors")

            colors = await master_service.get_all_colors()

            return SuccessResponse.create(
                data=colors, message="Colors retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Colors retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving colors: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_all_qualities(
        self, master_service: MasterDataService = Depends(get_master_service)
    ) -> APIResponse[List[Quality]]:
        """Get all active qualities"""
        try:
            self.logger.debug("Getting all qualities")

            qualities = await master_service.get_all_qualities()

            return SuccessResponse.create(
                data=qualities, message="Qualities retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Qualities retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving qualities: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_all_master_data(
        self, master_service: MasterDataService = Depends(get_master_service)
    ) -> APIResponse[Dict]:
        """Get all master data for forms and dropdowns"""
        try:
            self.logger.debug("Getting all master data")

            master_data = await master_service.get_all_master_data()

            return SuccessResponse.create(
                data=master_data, message="Master data retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Master data retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving master data: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_color_by_id(
        self,
        color_id: int,
        master_service: MasterDataService = Depends(get_master_service),
    ) -> APIResponse[Color]:
        """Get color by ID"""
        try:
            self.logger.debug(f"Getting color by ID: {color_id}")

            color = await master_service.get_color_by_id(color_id)

            return SuccessResponse.create(
                data=color, message="Color retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Color retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving color: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_quality_by_id(
        self,
        quality_id: int,
        master_service: MasterDataService = Depends(get_master_service),
    ) -> APIResponse[Quality]:
        """Get quality by ID"""
        try:
            self.logger.debug(f"Getting quality by ID: {quality_id}")

            quality = await master_service.get_quality_by_id(quality_id)

            return SuccessResponse.create(
                data=quality, message="Quality retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Quality retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving quality: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def initialize_default_data(
        self, master_service: MasterDataService = Depends(get_master_service)
    ) -> APIResponse[dict]:
        """Initialize master data with default values"""
        try:
            self.logger.info("Initializing default master data")

            success = await master_service.initialize_default_data()

            return SuccessResponse.create(
                data={"initialized": success},
                message="Master data initialization completed successfully",
            )

        except HTTPException as e:
            self.logger.warning(f"Master data initialization failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error initializing master data: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
