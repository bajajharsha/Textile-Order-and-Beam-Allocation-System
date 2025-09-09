"""
Master Data Controller - API request handlers for Colors, Qualities, Cuts
"""

from fastapi import HTTPException
from usecases.master_usecase import MasterUseCase


class MasterController:
    """Master data API handlers"""

    def __init__(self):
        self.use_case = MasterUseCase()

    # Color operations
    async def create_color(self, color_data: dict) -> dict:
        """Handle create color request"""
        try:
            color = await self.use_case.create_color(color_data)
            return color.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_color(self, color_id: int) -> dict:
        """Handle get color request"""
        try:
            color = await self.use_case.get_color(color_id)
            return color.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def update_color(self, color_id: int, update_data: dict) -> dict:
        """Handle update color request"""
        try:
            color = await self.use_case.update_color(color_id, update_data)
            return color.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def delete_color(self, color_id: int) -> dict:
        """Handle delete color request"""
        try:
            success = await self.use_case.delete_color(color_id)
            return {"success": success, "message": "Color deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def list_colors(self, page: int = 1, page_size: int = 20) -> dict:
        """Handle list colors request"""
        try:
            result = await self.use_case.list_colors(page, page_size)
            result["colors"] = [color.to_dict() for color in result["colors"]]
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def search_colors(self, query: str, limit: int = 20) -> dict:
        """Handle search colors request"""
        try:
            colors = await self.use_case.search_colors(query, limit)
            return {
                "colors": [color.to_dict() for color in colors],
                "total": len(colors),
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_colors_dropdown(self) -> dict:
        """Handle get colors dropdown request"""
        try:
            colors = await self.use_case.get_colors_dropdown()
            return {"colors": [color.to_dict() for color in colors]}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    # Quality operations
    async def create_quality(self, quality_data: dict) -> dict:
        """Handle create quality request"""
        try:
            quality = await self.use_case.create_quality(quality_data)
            return quality.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_quality(self, quality_id: int) -> dict:
        """Handle get quality request"""
        try:
            quality = await self.use_case.get_quality(quality_id)
            return quality.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def update_quality(self, quality_id: int, update_data: dict) -> dict:
        """Handle update quality request"""
        try:
            quality = await self.use_case.update_quality(quality_id, update_data)
            return quality.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def delete_quality(self, quality_id: int) -> dict:
        """Handle delete quality request"""
        try:
            success = await self.use_case.delete_quality(quality_id)
            return {"success": success, "message": "Quality deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def list_qualities(self, page: int = 1, page_size: int = 20) -> dict:
        """Handle list qualities request"""
        try:
            result = await self.use_case.list_qualities(page, page_size)
            result["qualities"] = [quality.to_dict() for quality in result["qualities"]]
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def search_qualities(self, query: str, limit: int = 20) -> dict:
        """Handle search qualities request"""
        try:
            qualities = await self.use_case.search_qualities(query, limit)
            return {
                "qualities": [quality.to_dict() for quality in qualities],
                "total": len(qualities),
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_qualities_dropdown(self) -> dict:
        """Handle get qualities dropdown request"""
        try:
            qualities = await self.use_case.get_qualities_dropdown()
            return {"qualities": [quality.to_dict() for quality in qualities]}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    # Cut operations
    async def create_cut(self, cut_data: dict) -> dict:
        """Handle create cut request"""
        try:
            cut = await self.use_case.create_cut(cut_data)
            return cut.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_cut(self, cut_id: int) -> dict:
        """Handle get cut request"""
        try:
            cut = await self.use_case.get_cut(cut_id)
            return cut.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def update_cut(self, cut_id: int, update_data: dict) -> dict:
        """Handle update cut request"""
        try:
            cut = await self.use_case.update_cut(cut_id, update_data)
            return cut.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def delete_cut(self, cut_id: int) -> dict:
        """Handle delete cut request"""
        try:
            success = await self.use_case.delete_cut(cut_id)
            return {"success": success, "message": "Cut deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def list_cuts(self, page: int = 1, page_size: int = 20) -> dict:
        """Handle list cuts request"""
        try:
            result = await self.use_case.list_cuts(page, page_size)
            result["cuts"] = [cut.to_dict() for cut in result["cuts"]]
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def search_cuts(self, query: str, limit: int = 20) -> dict:
        """Handle search cuts request"""
        try:
            cuts = await self.use_case.search_cuts(query, limit)
            return {"cuts": [cut.to_dict() for cut in cuts], "total": len(cuts)}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_cuts_dropdown(self) -> dict:
        """Handle get cuts dropdown request"""
        try:
            cuts = await self.use_case.get_cuts_dropdown()
            return {"cuts": [cut.to_dict() for cut in cuts]}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    # Combined dropdown data
    async def get_dropdown_data(self) -> dict:
        """Handle get all dropdown data request"""
        try:
            return await self.use_case.get_dropdown_data()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )
