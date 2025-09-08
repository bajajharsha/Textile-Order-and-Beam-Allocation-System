"""
Party service for business logic operations
Layer 2: Business Logic Layer
"""

from typing import Dict, List, Optional
from fastapi import HTTPException, status

from config.logging import get_logger
from models.party import PartyCreate, PartyUpdate, PartyResponse, PartySearch
from repositories.party_repository import PartyRepository


class PartyService:
    """Service for party business logic operations"""

    def __init__(self):
        self.party_repo = PartyRepository()
        self.logger = get_logger("services.party")

    async def create_party(self, party_data: PartyCreate) -> PartyResponse:
        """Create a new party with validation"""
        try:
            self.logger.info(f"Creating new party: {party_data.party_name}")

            # Validate party data
            validation_result = await self.party_repo.validate_party_data(
                party_name=party_data.party_name,
                gst=party_data.gst
            )

            if not validation_result["is_valid"]:
                self.logger.warning(f"Party validation failed: {validation_result['errors']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation_result["errors"]
                )

            # Convert Pydantic model to dict
            party_dict = party_data.dict()
            
            # Create party
            created_party = await self.party_repo.create(party_dict)
            
            self.logger.info(f"Successfully created party with ID: {created_party['id']}")
            
            return PartyResponse(**created_party)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating party: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create party"
            )

    async def get_party_by_id(self, party_id: int) -> PartyResponse:
        """Get party by ID"""
        try:
            self.logger.debug(f"Fetching party with ID: {party_id}")

            party = await self.party_repo.get_by_id(party_id)
            
            if not party:
                self.logger.warning(f"Party not found with ID: {party_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Party not found"
                )

            return PartyResponse(**party)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching party by ID {party_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch party"
            )

    async def get_all_parties(self, include_inactive: bool = False) -> List[PartyResponse]:
        """Get all parties"""
        try:
            self.logger.debug(f"Fetching all parties (include_inactive: {include_inactive})")

            if include_inactive:
                parties = await self.party_repo.get_all()
            else:
                parties = await self.party_repo.get_active_parties()

            party_responses = [PartyResponse(**party) for party in parties]
            
            self.logger.debug(f"Retrieved {len(party_responses)} parties")
            
            return party_responses

        except Exception as e:
            self.logger.error(f"Error fetching all parties: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch parties"
            )

    async def update_party(self, party_id: int, party_data: PartyUpdate) -> PartyResponse:
        """Update existing party"""
        try:
            self.logger.info(f"Updating party with ID: {party_id}")

            # Check if party exists
            existing_party = await self.party_repo.get_by_id(party_id)
            if not existing_party:
                self.logger.warning(f"Party not found for update: {party_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Party not found"
                )

            # Validate updated data if name or GST is being changed
            update_data = party_data.dict(exclude_unset=True)
            
            if "party_name" in update_data or "gst" in update_data:
                validation_result = await self.party_repo.validate_party_data(
                    party_name=update_data.get("party_name", existing_party["party_name"]),
                    gst=update_data.get("gst"),
                    exclude_id=party_id
                )

                if not validation_result["is_valid"]:
                    self.logger.warning(f"Party validation failed for update: {validation_result['errors']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=validation_result["errors"]
                    )

            # Update party
            updated_party = await self.party_repo.update(party_id, update_data)
            
            if not updated_party:
                self.logger.error(f"Failed to update party: {party_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update party"
                )

            self.logger.info(f"Successfully updated party: {party_id}")
            
            return PartyResponse(**updated_party)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating party {party_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update party"
            )

    async def delete_party(self, party_id: int) -> bool:
        """Delete party (soft delete)"""
        try:
            self.logger.info(f"Deleting party with ID: {party_id}")

            # Check if party exists
            existing_party = await self.party_repo.get_by_id(party_id)
            if not existing_party:
                self.logger.warning(f"Party not found for deletion: {party_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Party not found"
                )

            # TODO: Check if party has associated orders before deletion
            # For now, we'll allow deletion (soft delete)

            # Perform soft delete
            success = await self.party_repo.delete(party_id, soft_delete=True)
            
            if success:
                self.logger.info(f"Successfully deleted party: {party_id}")
            else:
                self.logger.error(f"Failed to delete party: {party_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete party"
                )

            return success

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting party {party_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete party"
            )

    async def search_parties(self, search_params: PartySearch) -> List[PartyResponse]:
        """Search parties based on criteria"""
        try:
            self.logger.debug(f"Searching parties with params: {search_params}")

            if search_params.search_term:
                parties = await self.party_repo.search_parties(
                    search_term=search_params.search_term,
                    include_inactive=search_params.include_inactive
                )
            else:
                # If no search term, apply filters
                filters = {"is_active": True} if not search_params.include_inactive else {}
                parties = await self.party_repo.get_all(filters=filters)

            # Apply additional filters
            if search_params.has_gst is not None:
                if search_params.has_gst:
                    parties = [p for p in parties if p.get("gst")]
                else:
                    parties = [p for p in parties if not p.get("gst")]

            if search_params.has_broker is not None:
                if search_params.has_broker:
                    parties = [p for p in parties if p.get("broker_name")]
                else:
                    parties = [p for p in parties if not p.get("broker_name")]

            party_responses = [PartyResponse(**party) for party in parties]
            
            self.logger.debug(f"Search found {len(party_responses)} parties")
            
            return party_responses

        except Exception as e:
            self.logger.error(f"Error searching parties: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search parties"
            )

    async def get_party_statistics(self) -> Dict:
        """Get party statistics for dashboard"""
        try:
            self.logger.debug("Fetching party statistics")

            stats = await self.party_repo.get_party_statistics()
            
            self.logger.debug("Successfully retrieved party statistics")
            
            return stats

        except Exception as e:
            self.logger.error(f"Error fetching party statistics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch party statistics"
            )

    async def get_parties_for_dropdown(self) -> List[Dict]:
        """Get simplified party list for dropdown menus"""
        try:
            self.logger.debug("Fetching parties for dropdown")

            parties = await self.party_repo.get_active_parties()
            
            # Return simplified format for dropdowns
            dropdown_parties = [
                {
                    "id": party["id"],
                    "party_name": party["party_name"],
                    "contact_number": party.get("contact_number", ""),
                    "broker_name": party.get("broker_name", "")
                }
                for party in parties
            ]

            self.logger.debug(f"Retrieved {len(dropdown_parties)} parties for dropdown")
            
            return dropdown_parties

        except Exception as e:
            self.logger.error(f"Error fetching parties for dropdown: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch parties for dropdown"
            )

    async def validate_party_data(
        self, 
        party_name: str, 
        gst: Optional[str] = None, 
        exclude_id: Optional[int] = None
    ) -> Dict:
        """Validate party data for frontend"""
        try:
            self.logger.debug(f"Validating party data: {party_name}")

            validation_result = await self.party_repo.validate_party_data(
                party_name=party_name,
                gst=gst,
                exclude_id=exclude_id
            )

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating party data: {str(e)}")
            return {
                "party_name_exists": False,
                "gst_exists": False,
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
