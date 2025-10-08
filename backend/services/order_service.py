"""
Order service for business logic operations
Layer 2: Business Logic Layer
"""

from decimal import Decimal
from typing import Dict, List, Optional

from config.logging import get_logger
from fastapi import HTTPException, status
from models.order import OrderCreate, OrderResponse
from repositories.order_repository import OrderRepository
from services.calculation_service import CalculationService
from services.design_service import DesignService


class OrderService:
    """Service for order business logic operations"""

    def __init__(self):
        self.order_repo = OrderRepository()
        self.calc_service = CalculationService()
        self.design_service = DesignService()
        self.logger = get_logger("services.order")

    def _generate_order_number(self) -> str:
        """Generate unique order number"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"

    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Create a new order with automatic calculations"""
        try:
            self.logger.info(f"Creating new order for party ID: {order_data.party_id}")

            # Validate order calculations
            order_dict = order_data.dict()
            validation_result = self.calc_service.validate_order_calculations(
                order_dict
            )

            if not validation_result["is_valid"]:
                self.logger.warning(
                    f"Order validation failed: {validation_result['errors']}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation_result["errors"],
                )

            # Generate order number
            order_number = self._generate_order_number()

            # Calculate total designs
            design_numbers = {item.design_number for item in order_data.order_items}
            total_designs = len(design_numbers)

            # Prepare order data
            order_dict = order_data.dict(exclude={"order_items"})
            order_dict.update(
                {"order_number": order_number, "total_designs": total_designs}
            )

            # Create order with items
            created_order = await self.order_repo.create_order_with_items(
                order_dict, order_data.order_items, self.calc_service
            )

            self.logger.info(
                f"Successfully created order {order_number} with ID: {created_order['id']}"
            )

            # NEW: Initialize design tracking for set-based allocation
            await self._initialize_design_tracking(created_order, order_data)

            # Convert to response model
            return await self._convert_to_response(created_order)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating order: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create order",
            )

    async def get_order_by_id(self, order_id: int) -> OrderResponse:
        """Get order by ID with all details"""
        try:
            self.logger.debug(f"Fetching order with ID: {order_id}")

            order = await self.order_repo.get_order_with_items(order_id)

            if not order:
                self.logger.warning(f"Order not found with ID: {order_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                )

            return await self._convert_to_response(order)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching order by ID {order_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch order",
            )

    async def get_all_orders(
        self,
        party_id: Optional[int] = None,
        quality_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[OrderResponse]:
        """Get all orders with optional filtering"""
        try:
            self.logger.debug("Fetching all orders")

            filters = {}
            if party_id:
                filters["party_id"] = party_id
            if quality_id:
                filters["quality_id"] = quality_id

            orders = await self.order_repo.get_all_orders_with_details(
                filters=filters, limit=limit, offset=offset
            )

            order_responses = []
            for order in orders:
                order_response = await self._convert_to_response(order)
                order_responses.append(order_response)

            self.logger.debug(f"Retrieved {len(order_responses)} orders")
            return order_responses

        except Exception as e:
            self.logger.error(f"Error fetching all orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch orders",
            )

    async def get_quality_wise_summary(self) -> Dict:
        """Get quality-wise beam summary for reporting"""
        try:
            self.logger.debug("Generating quality-wise beam summary")

            orders_data = await self.order_repo.get_orders_for_quality_summary()
            summary = self.calc_service.generate_quality_wise_summary(orders_data)

            self.logger.debug("Successfully generated quality-wise summary")
            return summary

        except Exception as e:
            self.logger.error(f"Error generating quality-wise summary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate quality-wise summary",
            )

    async def _convert_to_response(self, order_data: Dict) -> OrderResponse:
        """Convert order data from repository to response model"""
        try:
            # Calculate totals
            order_items = order_data.get("order_items", [])
            total_pieces = sum(item.get("calculated_pieces", 0) for item in order_items)

            rate_per_piece = Decimal(str(order_data.get("rate_per_piece", 0)))
            total_value = self.calc_service.calculate_order_value(
                total_pieces, rate_per_piece
            )

            # Add calculated fields
            order_data.update(
                {"total_pieces": total_pieces, "total_value": total_value}
            )

            return OrderResponse(**order_data)

        except Exception as e:
            self.logger.error(f"Error converting order to response: {str(e)}")
            raise

    async def _initialize_design_tracking(
        self, created_order: Dict, order_data: OrderCreate
    ) -> None:
        """Initialize design tracking tables for set-based allocation"""
        try:
            order_id = created_order["id"]
            sets = order_data.sets

            # Get unique design numbers from order items
            design_numbers = set()
            design_beam_map = {}  # design_number -> list of (beam_color_id, count)

            for item in order_data.order_items:
                design_numbers.add(item.design_number)

                # Track beam colors per design
                if item.design_number not in design_beam_map:
                    design_beam_map[item.design_number] = {}

                # Count beam color occurrences (this becomes beam_multiplier)
                beam_id = item.beam_color_id
                if beam_id in design_beam_map[item.design_number]:
                    design_beam_map[item.design_number][beam_id] += 1
                else:
                    design_beam_map[item.design_number][beam_id] = 1

            # Create design tracking and beam config for each design
            for design_number in design_numbers:
                # Create design set tracking
                await self.design_service.create_design_tracking(
                    order_id=order_id, design_number=design_number, total_sets=sets
                )

                # Create beam configurations for this design
                if design_number in design_beam_map:
                    for beam_color_id, multiplier in design_beam_map[
                        design_number
                    ].items():
                        await self.design_service.create_beam_config(
                            order_id=order_id,
                            design_number=design_number,
                            beam_color_id=beam_color_id,
                            beam_multiplier=multiplier,
                        )

            self.logger.info(
                f"Initialized design tracking for order {order_id}: "
                f"{len(design_numbers)} designs, {sets} sets each"
            )

        except Exception as e:
            # Log but don't fail order creation
            self.logger.warning(
                f"Failed to initialize design tracking for order {order_id}: {str(e)}"
            )
            # Not raising exception to avoid breaking existing order creation flow
