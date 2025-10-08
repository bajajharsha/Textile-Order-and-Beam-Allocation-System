"""
Design Service - Business logic for design tracking and beam allocation
Layer 2: Business Logic Layer
"""

from typing import Dict, List, Optional

from config.logging import get_logger
from fastapi import HTTPException, status
from models.schemas.design import (
    BeamConfigResponse,
    CompleteBeamSummaryResponse,
    DesignAllocationDetail,
    DesignSetTrackingResponse,
    DesignWiseAllocationResponse,
    QualityBeamSummary,
)
from repositories.design_repository import DesignRepository


class DesignService:
    """Service for design tracking and beam allocation business logic"""

    def __init__(self):
        self.design_repo = DesignRepository()
        self.logger = get_logger("services.design")

    # ============================================
    # Design Set Tracking
    # ============================================

    async def create_design_tracking(
        self, order_id: int, design_number: str, total_sets: int
    ) -> DesignSetTrackingResponse:
        """Create design set tracking for an order"""
        try:
            self.logger.debug(
                f"Creating design tracking: Order {order_id}, Design {design_number}"
            )

            tracking = await self.design_repo.create_design_set_tracking(
                order_id, design_number, total_sets
            )

            return DesignSetTrackingResponse(**tracking.to_dict())

        except Exception as e:
            self.logger.error(f"Error creating design tracking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create design tracking",
            )

    async def get_design_tracking(
        self, order_id: int, design_number: Optional[str] = None
    ) -> List[DesignSetTrackingResponse]:
        """Get design set tracking for an order"""
        try:
            self.logger.debug(f"Fetching design tracking for order {order_id}")

            trackings = await self.design_repo.get_design_set_tracking(
                order_id, design_number
            )

            return [DesignSetTrackingResponse(**t) for t in trackings]

        except Exception as e:
            self.logger.error(f"Error fetching design tracking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch design tracking",
            )

    async def allocate_sets(
        self, order_id: int, design_number: str, sets_to_allocate: int
    ) -> Dict:
        """Allocate sets to a design (called when creating lot)"""
        try:
            self.logger.info(
                f"Allocating {sets_to_allocate} sets for Order {order_id}, Design {design_number}"
            )

            success = await self.design_repo.update_allocated_sets(
                order_id, design_number, sets_to_allocate
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Design tracking not found for {design_number}",
                )

            return {
                "success": True,
                "message": f"Successfully allocated {sets_to_allocate} sets to {design_number}",
            }

        except ValueError as e:
            # Insufficient sets error
            self.logger.warning(f"Allocation validation error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error allocating sets: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to allocate sets",
            )

    # ============================================
    # Design Beam Configuration
    # ============================================

    async def create_beam_config(
        self,
        order_id: int,
        design_number: str,
        beam_color_id: int,
        beam_multiplier: int,
    ) -> BeamConfigResponse:
        """Create beam configuration for a design"""
        try:
            self.logger.debug(
                f"Creating beam config: Order {order_id}, Design {design_number}, "
                f"Beam {beam_color_id}, Multiplier {beam_multiplier}"
            )

            config = await self.design_repo.create_design_beam_config(
                order_id, design_number, beam_color_id, beam_multiplier
            )

            return BeamConfigResponse(**config.to_dict())

        except Exception as e:
            self.logger.error(f"Error creating beam config: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create beam configuration",
            )

    async def get_beam_config(
        self, order_id: int, design_number: Optional[str] = None
    ) -> List[BeamConfigResponse]:
        """Get beam configurations for designs"""
        try:
            self.logger.debug(f"Fetching beam configs for order {order_id}")

            configs = await self.design_repo.get_design_beam_config(
                order_id, design_number
            )

            return [BeamConfigResponse(**c) for c in configs]

        except Exception as e:
            self.logger.error(f"Error fetching beam configs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch beam configurations",
            )

    # ============================================
    # Design-Wise Allocation Reports
    # ============================================

    async def get_design_wise_allocation(
        self, order_id: Optional[int] = None, party_id: Optional[int] = None
    ) -> DesignWiseAllocationResponse:
        """Get design-wise beam allocation table (NEW TABLE)"""
        try:
            self.logger.debug("Generating design-wise allocation report")

            designs_data = await self.design_repo.get_design_wise_allocation_detail(
                order_id, party_id
            )

            print(designs_data)

            # Convert to response models
            designs = [DesignAllocationDetail(**d) for d in designs_data]

            # Calculate totals
            total_designs = len(designs)
            total_remaining_sets = sum(d.remaining_sets for d in designs)

            self.logger.info(
                f"Generated design-wise allocation: {total_designs} designs, "
                f"{total_remaining_sets} total remaining sets"
            )

            return DesignWiseAllocationResponse(
                designs=designs,
                total_designs=total_designs,
                total_remaining_sets=total_remaining_sets,
            )

        except Exception as e:
            self.logger.error(f"Error generating design-wise allocation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate design-wise allocation report",
            )

    async def get_complete_beam_summary(self) -> CompleteBeamSummaryResponse:
        """Get complete beam allocation table (ALL DESIGNS AGGREGATED)"""
        try:
            self.logger.debug("Generating complete beam summary (aggregated)")

            qualities_data = await self.design_repo.get_complete_beam_summary()

            # Convert to response models
            qualities = [QualityBeamSummary(**q) for q in qualities_data]

            # Calculate grand total
            grand_total_pieces = sum(q.total_pieces for q in qualities)

            self.logger.info(
                f"Generated complete beam summary: {len(qualities)} qualities, "
                f"{grand_total_pieces} total pieces"
            )

            return CompleteBeamSummaryResponse(
                qualities=qualities, grand_total_pieces=grand_total_pieces
            )

        except Exception as e:
            self.logger.error(f"Error generating complete beam summary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate complete beam summary",
            )

    # ============================================
    # Helper Methods
    # ============================================

    async def validate_design_allocation(
        self, order_id: int, design_number: str, requested_sets: int
    ) -> Dict:
        """Validate if requested sets can be allocated"""
        try:
            trackings = await self.design_repo.get_design_set_tracking(
                order_id, design_number
            )

            if not trackings:
                return {
                    "valid": False,
                    "error": f"Design {design_number} not found for order {order_id}",
                }

            tracking = trackings[0]
            remaining_sets = tracking["remaining_sets"]

            if requested_sets > remaining_sets:
                return {
                    "valid": False,
                    "error": f"Insufficient sets. Available: {remaining_sets}, Requested: {requested_sets}",
                }

            return {
                "valid": True,
                "remaining_sets": remaining_sets,
                "available_after_allocation": remaining_sets - requested_sets,
            }

        except Exception as e:
            self.logger.error(f"Error validating design allocation: {str(e)}")
            return {"valid": False, "error": str(e)}

    async def get_designs_by_order(self, order_id: int) -> List[str]:
        """Get list of design numbers for an order"""
        try:
            return await self.design_repo.get_designs_by_order(order_id)
        except Exception as e:
            self.logger.error(f"Error fetching designs for order: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch designs for order",
            )
