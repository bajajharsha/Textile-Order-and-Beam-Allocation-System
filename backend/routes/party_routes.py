"""
Party API Routes
"""

from controllers.party_controller import PartyController
from fastapi import APIRouter, Depends, Query
from models.schemas.party import PartyCreate, PartyUpdate

router = APIRouter()


@router.post("/")
async def create_party(
    party_data: PartyCreate,
    party_controller: PartyController = Depends(),
):
    """Create new party"""
    return await party_controller.create_party(party_data.dict())


@router.get("/{party_id}")
async def get_party(
    party_id: int,
    party_controller: PartyController = Depends(),
):
    """Get party by ID"""
    return await party_controller.get_party(party_id)


@router.put("/{party_id}")
async def update_party(
    party_id: int,
    update_data: PartyUpdate,
    party_controller: PartyController = Depends(),
):
    """Update party"""
    return await party_controller.update_party(party_id, update_data.dict())


@router.delete("/{party_id}")
async def delete_party(
    party_id: int,
    party_controller: PartyController = Depends(),
):
    """Delete party"""
    return await party_controller.delete_party(party_id)


@router.get("/", response_model=dict)
async def list_parties(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    party_controller: PartyController = Depends(),
):
    """List all parties with pagination"""
    return await party_controller.list_parties(page, page_size)


@router.get("/search/", response_model=dict)
async def search_parties(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    party_controller: PartyController = Depends(),
):
    """Search parties"""
    return await party_controller.search_parties(q, limit)
