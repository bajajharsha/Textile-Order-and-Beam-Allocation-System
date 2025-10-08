"""
Lot Service - Business logic layer for lot management
Layer 2: Business Logic Layer
"""

from typing import Dict, List, Optional

from config.logging import get_logger
from fastapi import HTTPException, status
from models.schemas.design import LotCreateFromSets
from models.schemas.lot import (
    AllocationSummary,
    BeamSummaryWithAllocation,
    LotCreate,
    LotRegisterResponse,
    LotResponse,
    LotUpdate,
    OrderItemStatusResponse,
    PartywiseDetailResponse,
)
from services.design_service import DesignService
from usecases.lot_usecase import LotUseCase


class LotService:
    """Service for lot business logic operations"""

    def __init__(self):
        self.lot_usecase = LotUseCase()
        self.design_service = DesignService()
        self.logger = get_logger("services.lot")

    async def create_lot(self, lot_data: LotCreate) -> LotResponse:
        """Create new lot with allocations"""
        try:
            self.logger.debug("Creating new lot")

            # Convert Pydantic model to dict
            lot_dict = lot_data.model_dump()

            # Create lot
            created_lot = await self.lot_usecase.create_lot(lot_dict)

            self.logger.info(f"Successfully created lot {created_lot['lot_number']}")
            return LotResponse(**created_lot)

        except ValueError as e:
            self.logger.warning(f"Validation error creating lot: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            self.logger.error(f"Error creating lot: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create lot",
            )

    async def create_lot_from_sets(self, lot_data: LotCreateFromSets) -> Dict:
        """Create lot using set-based allocation (NEW METHOD for design-wise lots)"""
        try:
            self.logger.info("Creating lot with set-based allocations")

            # Validate: Check if sufficient sets available for each design
            for allocation in lot_data.design_allocations:
                validation = await self.design_service.validate_design_allocation(
                    allocation.order_id,
                    allocation.design_number,
                    allocation.allocated_sets,
                )

                if not validation["valid"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=validation["error"],
                    )

            # Create the lot (reuse existing lot creation logic)
            lot_dict = {
                "party_id": lot_data.party_id,
                "quality_id": lot_data.quality_id,
                "lot_date": lot_data.lot_date,
                "lot_number": lot_data.lot_number,
                "bill_number": lot_data.bill_number,
                "actual_pieces": lot_data.actual_pieces,
                "delivery_date": lot_data.delivery_date,
                "notes": lot_data.notes,
                "allocations": [],  # Will be empty for now, we handle separately
            }

            # Create lot through existing use case
            lot = await self.lot_usecase.create_lot(lot_dict)
            lot_id = lot.get("id")

            # Create lot_design_allocations entries for each design
            from config.database import database, get_ist_timestamp

            client = await database.get_client()

            for allocation in lot_data.design_allocations:
                # Create lot_design_allocation entry
                allocation_data = {
                    "lot_id": lot_id,
                    "order_id": allocation.order_id,
                    "design_number": allocation.design_number,
                    "allocated_sets": allocation.allocated_sets,
                    "created_at": get_ist_timestamp(),
                    "updated_at": get_ist_timestamp(),
                }
                client.table("lot_design_allocations").insert(allocation_data).execute()

                # Update design set tracking
                await self.design_service.allocate_sets(
                    allocation.order_id,
                    allocation.design_number,
                    allocation.allocated_sets,
                )

            self.logger.info(
                f"Successfully created lot with {len(lot_data.design_allocations)} design allocations"
            )

            return {
                "success": True,
                "lot": lot,
                "message": f"Lot created successfully with {len(lot_data.design_allocations)} design allocations",
            }

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating lot from sets: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create lot from sets: {str(e)}",
            )

    async def get_lot_by_id(self, lot_id: int) -> LotResponse:
        """Get lot by ID with details"""
        try:
            self.logger.debug(f"Fetching lot with ID: {lot_id}")

            lot = await self.lot_usecase.get_lot_details(lot_id)

            if not lot:
                self.logger.warning(f"Lot not found with ID: {lot_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found"
                )

            return LotResponse(**lot)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching lot by ID {lot_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch lot",
            )

    async def get_all_lots(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """Get all lots with pagination"""
        try:
            self.logger.debug("Fetching all lots")

            result = await self.lot_usecase.get_all_lots(page, page_size)

            # Convert lots to response models
            lots = [LotResponse(**lot) for lot in result["lots"]]

            return {
                "lots": lots,
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
            }

        except Exception as e:
            self.logger.error(f"Error fetching all lots: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch lots",
            )

    async def update_lot(self, lot_id: int, update_data: LotUpdate) -> LotResponse:
        """Update lot"""
        try:
            self.logger.debug(f"Updating lot {lot_id}")

            # Convert to dict, excluding None values
            update_dict = update_data.model_dump(exclude_none=True)

            updated_lot = await self.lot_usecase.update_lot(lot_id, update_dict)

            if not updated_lot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lot not found",
                )

            self.logger.info(f"Successfully updated lot {lot_id}")
            return LotResponse(**updated_lot)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating lot {lot_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update lot",
            )

    async def delete_lot(self, lot_id: int) -> Dict:
        """Delete lot"""
        try:
            self.logger.debug(f"Deleting lot {lot_id}")

            success = await self.lot_usecase.delete_lot(lot_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lot not found",
                )

            self.logger.info(f"Successfully deleted lot {lot_id}")
            return {"success": True, "message": "Lot deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting lot {lot_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete lot",
            )

    async def get_partywise_detail(self, party_id: Optional[int] = None) -> Dict:
        """Get partywise detail (red book) report"""
        try:
            self.logger.debug("Generating partywise detail report")

            result = await self.lot_usecase.get_partywise_detail(party_id)

            # Convert to response models
            parties = []
            for party_data in result["parties"]:
                party_response = PartywiseDetailResponse(**party_data)
                parties.append(party_response)

            return {
                "parties": parties,
                "total_parties": result["total_parties"],
                "grand_total_pieces": result["grand_total_pieces"],
            }

        except Exception as e:
            self.logger.error(f"Error generating partywise detail: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate partywise detail report",
            )

    async def get_lot_register(
        self,
        page: int = 1,
        page_size: int = 20,
        lot_register_type: Optional[str] = None,
    ) -> LotRegisterResponse:
        """Get lot register report"""
        try:
            self.logger.debug("Generating lot register report")

            result = await self.lot_usecase.get_lot_register(
                page, page_size, lot_register_type
            )

            return LotRegisterResponse(**result)

        except Exception as e:
            self.logger.error(f"Error generating lot register: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate lot register report",
            )

    async def get_order_allocation_status(
        self, order_id: Optional[int] = None
    ) -> List[OrderItemStatusResponse]:
        """Get order item allocation status"""
        try:
            self.logger.debug("Fetching order allocation status")

            status_items = await self.lot_usecase.get_order_allocation_status(order_id)

            return [OrderItemStatusResponse(**item) for item in status_items]

        except Exception as e:
            self.logger.error(f"Error fetching order allocation status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch order allocation status",
            )

    async def get_beam_summary_with_allocation(self) -> Dict:
        """Get beam summary with allocation details"""
        try:
            self.logger.debug("Generating beam summary with allocation")

            result = await self.lot_usecase.get_beam_summary_with_allocation()

            # Convert to response models
            qualities = []
            for quality_data in result["qualities"]:
                quality_items = [
                    BeamSummaryWithAllocation(**item) for item in quality_data["items"]
                ]
                qualities.append(
                    {
                        **quality_data,
                        "items": quality_items,
                    }
                )

            return {
                "qualities": qualities,
                "summary": AllocationSummary(**result["summary"]),
            }

        except Exception as e:
            self.logger.error(
                f"Error generating beam summary with allocation: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate beam summary with allocation",
            )

    async def get_available_allocations(
        self,
        party_id: Optional[int] = None,
        quality_id: Optional[int] = None,
    ) -> List[OrderItemStatusResponse]:
        """Get available items for allocation"""
        try:
            self.logger.debug("Fetching available allocations")

            available_items = await self.lot_usecase.get_available_allocations(
                party_id, quality_id
            )

            return [OrderItemStatusResponse(**item) for item in available_items]

        except Exception as e:
            self.logger.error(f"Error fetching available allocations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch available allocations",
            )

    async def initialize_order_status(self, order_id: int) -> Dict:
        """Initialize order item status after order creation"""
        try:
            self.logger.debug(f"Initializing order status for order {order_id}")

            await self.lot_usecase.initialize_order_status(order_id)

            return {"success": True, "message": "Order status initialized successfully"}

        except Exception as e:
            self.logger.error(f"Error initializing order status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize order status",
            )

    async def update_lot_field(self, lot_id: int, field: str, value: str) -> Dict:
        """Update a specific field of a lot (for inline editing)"""
        try:
            self.logger.debug(f"Updating lot {lot_id} field {field} to {value}")

            success = await self.lot_usecase.update_lot_field(lot_id, field, value)

            if success:
                return {
                    "success": True,
                    "message": f"Successfully updated {field} for lot {lot_id}",
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Lot {lot_id} not found",
                )

        except ValueError as e:
            self.logger.warning(f"Validation error updating lot field: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            self.logger.error(f"Error updating lot field: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update lot field",
            )

    async def create_lot_from_register(self, lot_data: dict) -> Dict:
        """Create a lot when lot number is entered in the register"""
        try:
            self.logger.debug(f"Creating lot from register: {lot_data}")

            created_lot = await self.lot_usecase.create_lot_from_register(
                lot_data["order_id"],
                lot_data["lot_number"],
                lot_data["lot_date"],
                lot_data["party_id"],
                lot_data["quality_id"],
            )

            return {
                "success": True,
                "message": f"Successfully created lot {lot_data['lot_number']}",
                "lot": created_lot,
            }

        except ValueError as e:
            self.logger.warning(
                f"Validation error creating lot from register: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            self.logger.error(f"Error creating lot from register: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create lot from register",
            )

    async def create_lot_for_design(self, lot_data: dict) -> Dict:
        """Create a lot for a specific design when lot number is entered in the register"""
        try:
            self.logger.debug(f"Creating lot for design: {lot_data}")

            created_lot = await self.lot_usecase.create_lot_for_design(
                lot_data["order_id"],
                lot_data["design_number"],
                lot_data["lot_number"],
                lot_data["lot_date"],
                lot_data["party_id"],
                lot_data["quality_id"],
                lot_data.get("bill_number"),
                lot_data.get("actual_pieces"),
                lot_data.get("delivery_date"),
            )

            return {
                "success": True,
                "message": f"Successfully created lot {lot_data['lot_number']} for design {lot_data['design_number']}",
                "lot": created_lot,
            }

        except ValueError as e:
            self.logger.warning(f"Validation error creating lot for design: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            self.logger.error(f"Error creating lot for design: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create lot for design",
            )

    async def create_lot_from_design(self, lot_data: dict) -> Dict:
        """Create a lot from design selection form with piece reduction logic"""
        try:
            self.logger.debug(f"Creating lot from design form: {lot_data}")

            created_lot = await self.lot_usecase.create_lot_from_design(
                lot_data["order_id"],
                lot_data["lot_number"],
                lot_data["lot_date"],
                lot_data["design_number"],
                lot_data["pieces_allocated"],
            )

            return {
                "success": True,
                "message": f"Lot {lot_data['lot_number']} created successfully for design {lot_data['design_number']}",
                "lot": created_lot,
            }

        except Exception as e:
            self.logger.error(f"Error creating lot from design: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create lot from design",
            )
