"""
Master Data API Routes - Colors, Qualities, Cuts
"""

from controllers.master_controller import MasterController
from fastapi import APIRouter, Depends, Query
from models.schemas.color import ColorCreate, ColorUpdate
from models.schemas.cut import CutCreate, CutUpdate
from models.schemas.quality import QualityCreate, QualityUpdate

router = APIRouter()


# Combined dropdown endpoint
@router.get("/dropdown-data")
async def get_dropdown_data(
    master_controller: MasterController = Depends(MasterController),
):
    """Get all dropdown data for order form"""
    return await master_controller.get_dropdown_data()


# Color routes
@router.post("/colors/")
async def create_color(
    color_data: ColorCreate,
    master_controller: MasterController = Depends(MasterController),
):
    """Create new color"""
    return await master_controller.create_color(color_data.dict())


@router.get("/colors/{color_id}")
async def get_color(color_id: int, master_controller: MasterController = Depends()):
    """Get color by ID"""
    return await master_controller.get_color(color_id)


@router.put("/colors/{color_id}")
async def update_color(
    color_id: int,
    update_data: ColorUpdate,
    master_controller: MasterController = Depends(MasterController),
):
    """Update color"""
    return await master_controller.update_color(
        color_id, update_data.dict(exclude_unset=True)
    )


@router.delete("/colors/{color_id}")
async def delete_color(color_id: int, master_controller: MasterController = Depends()):
    """Delete color"""
    return await master_controller.delete_color(color_id)


@router.get("/colors/")
async def list_colors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    master_controller: MasterController = Depends(MasterController),
):
    """List all colors with pagination"""
    return await master_controller.list_colors(page, page_size)


@router.get("/colors/search/")
async def search_colors(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    master_controller: MasterController = Depends(MasterController),
):
    """Search colors"""
    return await master_controller.search_colors(q, limit)


@router.get("/colors/dropdown/")
async def get_colors_dropdown(
    master_controller: MasterController = Depends(MasterController),
):
    """Get colors for dropdown"""
    return await master_controller.get_colors_dropdown()


# Quality routes
@router.post("/qualities/")
async def create_quality(
    quality_data: QualityCreate,
    master_controller: MasterController = Depends(MasterController),
):
    """Create new quality"""
    return await master_controller.create_quality(quality_data.dict())


@router.get("/qualities/{quality_id}")
async def get_quality(
    quality_id: int,
    master_controller: MasterController = Depends(MasterController),
):
    """Get quality by ID"""
    return await master_controller.get_quality(quality_id)


@router.put("/qualities/{quality_id}")
async def update_quality(
    quality_id: int,
    update_data: QualityUpdate,
    master_controller: MasterController = Depends(MasterController),
):
    """Update quality"""
    return await master_controller.update_quality(
        quality_id, update_data.dict(exclude_unset=True)
    )


@router.delete("/qualities/{quality_id}")
async def delete_quality(
    quality_id: int,
    master_controller: MasterController = Depends(MasterController),
):
    """Delete quality"""
    return await master_controller.delete_quality(quality_id)


@router.get("/qualities/")
async def list_qualities(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    master_controller: MasterController = Depends(MasterController),
):
    """List all qualities with pagination"""
    return await master_controller.list_qualities(page, page_size)


@router.get("/qualities/search/")
async def search_qualities(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    master_controller: MasterController = Depends(MasterController),
):
    """Search qualities"""
    return await master_controller.search_qualities(q, limit)


@router.get("/qualities/dropdown/")
async def get_qualities_dropdown(
    master_controller: MasterController = Depends(MasterController),
):
    """Get qualities for dropdown"""
    return await master_controller.get_qualities_dropdown()


# Cut routes
@router.post("/cuts/")
async def create_cut(
    cut_data: CutCreate,
    master_controller: MasterController = Depends(MasterController),
):
    """Create new cut"""
    return await master_controller.create_cut(cut_data.dict())


@router.get("/cuts/{cut_id}")
async def get_cut(cut_id: int, master_controller: MasterController = Depends()):
    """Get cut by ID"""
    return await master_controller.get_cut(cut_id)


@router.put("/cuts/{cut_id}")
async def update_cut(
    cut_id: int,
    update_data: CutUpdate,
    master_controller: MasterController = Depends(MasterController),
):
    """Update cut"""
    return await master_controller.update_cut(
        cut_id, update_data.dict(exclude_unset=True)
    )


@router.delete("/cuts/{cut_id}")
async def delete_cut(cut_id: int, master_controller: MasterController = Depends()):
    """Delete cut"""
    return await master_controller.delete_cut(cut_id)


@router.get("/cuts/")
async def list_cuts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    master_controller: MasterController = Depends(MasterController),
):
    """List all cuts with pagination"""
    return await master_controller.list_cuts(page, page_size)


@router.get("/cuts/search/")
async def search_cuts(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    master_controller: MasterController = Depends(MasterController),
):
    """Search cuts"""
    return await master_controller.search_cuts(q, limit)


@router.get("/cuts/dropdown/")
async def get_cuts_dropdown(
    master_controller: MasterController = Depends(MasterController),
):
    """Get cuts for dropdown"""
    return await master_controller.get_cuts_dropdown()
