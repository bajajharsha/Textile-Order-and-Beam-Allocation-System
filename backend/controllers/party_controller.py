"""
Party Controller - API request handlers
"""

from fastapi import HTTPException
from usecases.party_usecase import PartyUseCase


class PartyController:
    """Party API handlers"""

    def __init__(self, use_case: PartyUseCase):
        self.use_case = use_case

    async def create_party(self, party_data: dict) -> dict:
        """Handle create party request"""
        try:
            party = await self.use_case.create_party(party_data)
            return party.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_party(self, party_id: int) -> dict:
        """Handle get party request"""
        try:
            party = await self.use_case.get_party(party_id)
            return party.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def update_party(self, party_id: int, update_data: dict) -> dict:
        """Handle update party request"""
        try:
            party = await self.use_case.update_party(party_id, update_data)
            return party.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def delete_party(self, party_id: int) -> bool:
        """Handle delete party request"""
        try:
            success = await self.use_case.delete_party(party_id)
            return success
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def list_parties(self, page: int = 1, page_size: int = 20) -> dict:
        """Handle list parties request"""
        try:
            result = await self.use_case.list_parties(page, page_size)
            # Convert domain models to dictionaries for serialization
            result["parties"] = [party.to_dict() for party in result["parties"]]
            return result
        except Exception as e:
            print(f"Error in list_parties: {str(e)}")  # Debug print
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def search_parties(self, query: str, limit: int = 20) -> dict:
        """Handle search parties request"""
        try:
            parties = await self.use_case.search_parties(query, limit)
            # Convert domain models to dictionaries for serialization
            parties_dict = [party.to_dict() for party in parties]
            return {"parties": parties_dict, "count": len(parties_dict)}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )
