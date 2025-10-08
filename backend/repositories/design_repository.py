"""
Design Repository - Database operations for design tracking and beam configuration
"""

import logging
from typing import Dict, List, Optional

from config.database import database, get_ist_timestamp
from models.domain.design import DesignBeamConfig, DesignSetTracking


class DesignRepository:
    """Design database operations"""

    def __init__(self):
        self.db_client = database
        self.logger = logging.getLogger(__name__)

    # ============================================
    # Design Set Tracking Operations
    # ============================================

    async def create_design_set_tracking(
        self, order_id: int, design_number: str, total_sets: int
    ) -> DesignSetTracking:
        """Create design set tracking entry"""
        client = await self.db_client.get_client()

        tracking_data = {
            "order_id": order_id,
            "design_number": design_number,
            "total_sets": total_sets,
            "allocated_sets": 0,
            "remaining_sets": total_sets,  # Initially, all sets are remaining
            "is_active": True,
            "created_at": get_ist_timestamp(),
            "updated_at": get_ist_timestamp(),
        }

        result = client.table("design_set_tracking").insert(tracking_data).execute()

        self.logger.info(
            f"Created design tracking: Order {order_id}, Design {design_number}, Sets {total_sets}"
        )

        return DesignSetTracking.from_dict(result.data[0])

    async def get_design_set_tracking(
        self, order_id: int, design_number: Optional[str] = None
    ) -> List[dict]:
        """Get design set tracking for an order"""
        client = await self.db_client.get_client()

        query = (
            client.table("design_set_tracking")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_active", True)
        )

        if design_number:
            query = query.eq("design_number", design_number)

        result = query.order("design_number").execute()

        return result.data

    async def update_allocated_sets(
        self, order_id: int, design_number: str, sets_to_allocate: int
    ) -> bool:
        """Update allocated and remaining sets when creating a lot"""
        client = await self.db_client.get_client()

        # First, get current tracking
        current = await self.get_design_set_tracking(order_id, design_number)
        if not current:
            self.logger.error(
                f"Design tracking not found: Order {order_id}, Design {design_number}"
            )
            return False

        tracking = current[0]
        new_allocated = tracking["allocated_sets"] + sets_to_allocate
        new_remaining = tracking["remaining_sets"] - sets_to_allocate

        # Validate
        if new_remaining < 0:
            self.logger.error(
                f"Insufficient sets: Order {order_id}, Design {design_number}, "
                f"Requested {sets_to_allocate}, Available {tracking['remaining_sets']}"
            )
            raise ValueError(
                f"Insufficient sets for {design_number}. "
                f"Available: {tracking['remaining_sets']}, Requested: {sets_to_allocate}"
            )

        # Update
        update_data = {
            "allocated_sets": new_allocated,
            "remaining_sets": new_remaining,
            "updated_at": get_ist_timestamp(),
        }

        result = (
            client.table("design_set_tracking")
            .update(update_data)
            .eq("order_id", order_id)
            .eq("design_number", design_number)
            .execute()
        )

        self.logger.info(
            f"Updated design tracking: Order {order_id}, Design {design_number}, "
            f"Allocated {new_allocated}, Remaining {new_remaining}"
        )

        return len(result.data) > 0

    # ============================================
    # Design Beam Configuration Operations
    # ============================================

    async def create_design_beam_config(
        self,
        order_id: int,
        design_number: str,
        beam_color_id: int,
        beam_multiplier: int,
    ) -> DesignBeamConfig:
        """Create beam configuration for a design"""
        client = await self.db_client.get_client()

        config_data = {
            "order_id": order_id,
            "design_number": design_number,
            "beam_color_id": beam_color_id,
            "beam_multiplier": beam_multiplier,
            "is_active": True,
            "created_at": get_ist_timestamp(),
        }

        result = client.table("design_beam_config").insert(config_data).execute()

        self.logger.info(
            f"Created beam config: Order {order_id}, Design {design_number}, "
            f"Beam {beam_color_id}, Multiplier {beam_multiplier}"
        )

        return DesignBeamConfig.from_dict(result.data[0])

    async def get_design_beam_config(
        self, order_id: int, design_number: Optional[str] = None
    ) -> List[dict]:
        """Get beam configurations for designs in an order"""
        client = await self.db_client.get_client()

        query = (
            client.table("design_beam_config")
            .select(
                """
                *,
                colors!inner(id, color_code, color_name)
            """
            )
            .eq("order_id", order_id)
            .eq("is_active", True)
        )

        if design_number:
            query = query.eq("design_number", design_number)

        result = query.order("design_number, beam_color_id").execute()

        # Process to flatten color data
        configs = []
        for item in result.data:
            config = {
                **item,
                "beam_color_code": item["colors"]["color_code"],
                "beam_color_name": item["colors"]["color_name"],
            }
            del config["colors"]
            configs.append(config)

        return configs

    # ============================================
    # Combined Queries for Reporting
    # ============================================

    async def get_design_wise_allocation_detail(
        self, order_id: Optional[int] = None, party_id: Optional[int] = None
    ) -> List[dict]:
        """Get complete design-wise allocation details with beam breakdown"""
        client = await self.db_client.get_client()

        # Build query with joins
        query = (
            client.table("design_set_tracking")
            .select(
                """
                *,
                orders!inner(
                    id, 
                    order_number, 
                    party_id, 
                    quality_id, 
                    rate_per_piece, 
                    lot_register_type,
                    is_active,
                    parties!inner(id, party_name),
                    qualities!inner(id, quality_name)
                )
            """
            )
            .eq("is_active", True)
            .eq("orders.is_active", True)
        )

        if order_id:
            query = query.eq("order_id", order_id)

        if party_id:
            query = query.eq("orders.party_id", party_id)

        result = query.order("design_number").execute()

        # Process and enrich with beam configs
        designs = []
        for item in result.data:
            # Get beam configs for this design
            beam_configs = await self.get_design_beam_config(
                item["order_id"], item["design_number"]
            )

            # Calculate beam pieces
            beam_pieces = []
            for config in beam_configs:
                pieces = item["remaining_sets"] * config["beam_multiplier"]
                beam_pieces.append(
                    {
                        "beam_color_code": config["beam_color_code"],
                        "beam_color_name": config["beam_color_name"],
                        "beam_multiplier": config["beam_multiplier"],
                        "pieces": pieces,
                    }
                )

            design_detail = {
                "order_id": item["order_id"],
                "order_number": item["orders"]["order_number"],
                "party_name": item["orders"]["parties"]["party_name"],
                "quality_name": item["orders"]["qualities"]["quality_name"],
                "lot_register_type": item["orders"]["lot_register_type"],
                "design_number": item["design_number"],
                "total_sets": item["total_sets"],
                "allocated_sets": item["allocated_sets"],
                "remaining_sets": item["remaining_sets"],
                "beam_pieces": beam_pieces,
            }

            designs.append(design_detail)

        return designs

    async def get_complete_beam_summary(self) -> List[dict]:
        """Get aggregated beam summary across all designs (grouped by quality)"""
        designs = await self.get_design_wise_allocation_detail()

        # Aggregate by quality and beam color
        quality_summary: Dict[str, Dict] = {}

        for design in designs:
            quality = design["quality_name"]

            if quality not in quality_summary:
                quality_summary[quality] = {
                    "quality_name": quality,
                    "beam_colors": {},
                    "total_pieces": 0,
                }

            # Aggregate beam pieces
            for beam in design["beam_pieces"]:
                color_key = beam["beam_color_code"]

                if color_key not in quality_summary[quality]["beam_colors"]:
                    quality_summary[quality]["beam_colors"][color_key] = {
                        "beam_color_code": beam["beam_color_code"],
                        "beam_color_name": beam["beam_color_name"],
                        "total_pieces": 0,
                        "designs_count": 0,
                    }

                quality_summary[quality]["beam_colors"][color_key]["total_pieces"] += (
                    beam["pieces"]
                )
                quality_summary[quality]["beam_colors"][color_key]["designs_count"] += 1
                quality_summary[quality]["total_pieces"] += beam["pieces"]

        # Convert to list format
        result = []
        for quality_data in quality_summary.values():
            quality_data["beam_colors"] = list(quality_data["beam_colors"].values())
            result.append(quality_data)

        return result

    async def get_designs_by_order(self, order_id: int) -> List[str]:
        """Get list of design numbers for an order"""
        client = await self.db_client.get_client()

        result = (
            client.table("design_set_tracking")
            .select("design_number")
            .eq("order_id", order_id)
            .eq("is_active", True)
            .order("design_number")
            .execute()
        )

        return [item["design_number"] for item in result.data]
