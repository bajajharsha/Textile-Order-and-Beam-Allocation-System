"""
Order controller for API request handling
Layer 1: Presentation Layer
"""

from typing import List, Optional

from config.logging import get_logger
from fastapi import Depends, HTTPException, Query
from models.base import APIResponse, SuccessResponse
from models.order import OrderCreate, OrderResponse, OrderSearch, OrderUpdate
from services.order_service import OrderService


class OrderController:
    """Controller for order API endpoints"""

    def __init__(self):
        self.logger = get_logger("controllers.order")

    def get_order_service(self) -> OrderService:
        """Dependency to get order service instance"""
        return OrderService()

    async def create_order(
        self,
        order_data: OrderCreate,
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[OrderResponse]:
        """Create a new order"""
        try:
            self.logger.info("Creating new order via API")

            created_order = await order_service.create_order(order_data)

            return SuccessResponse.create(
                data=created_order, message="Order created successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Order creation failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating order: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_order_by_id(
        self, order_id: int, order_service: OrderService = Depends(get_order_service)
    ) -> APIResponse[OrderResponse]:
        """Get order by ID"""
        try:
            self.logger.debug(f"Getting order by ID: {order_id}")

            order = await order_service.get_order_by_id(order_id)

            return SuccessResponse.create(
                data=order, message="Order retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Order retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving order: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_all_orders(
        self,
        party_id: Optional[int] = Query(None, description="Filter by party ID"),
        quality_id: Optional[int] = Query(None, description="Filter by quality ID"),
        limit: Optional[int] = Query(None, description="Limit number of results"),
        offset: Optional[int] = Query(None, description="Offset for pagination"),
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[List[OrderResponse]]:
        """Get all orders with optional filtering"""
        try:
            self.logger.debug("Getting all orders")

            orders = await order_service.get_all_orders(
                party_id=party_id, quality_id=quality_id, limit=limit, offset=offset
            )

            return SuccessResponse.create(
                data=orders, message="Orders retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Orders retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving orders: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def update_order(
        self,
        order_id: int,
        order_data: OrderUpdate,
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[OrderResponse]:
        """Update existing order"""
        try:
            self.logger.info(f"Updating order: {order_id}")

            updated_order = await order_service.update_order(order_id, order_data)

            return SuccessResponse.create(
                data=updated_order, message="Order updated successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Order update failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error updating order: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def search_orders(
        self,
        search_term: Optional[str] = Query(
            None, description="Search in order number, party name, or design numbers"
        ),
        party_id: Optional[int] = Query(None, description="Filter by specific party"),
        quality_id: Optional[int] = Query(
            None, description="Filter by specific quality"
        ),
        status: Optional[str] = Query(None, description="Filter by order status"),
        date_from: Optional[str] = Query(
            None, description="Filter orders from this date (YYYY-MM-DD)"
        ),
        date_to: Optional[str] = Query(
            None, description="Filter orders until this date (YYYY-MM-DD)"
        ),
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[List[OrderResponse]]:
        """Search orders based on criteria"""
        try:
            self.logger.debug(f"Searching orders with term: {search_term}")

            # Parse dates if provided
            parsed_date_from = None
            parsed_date_to = None

            if date_from:
                from datetime import datetime

                parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d").date()

            if date_to:
                from datetime import datetime

                parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

            search_params = OrderSearch(
                search_term=search_term,
                party_id=party_id,
                quality_id=quality_id,
                status=status,
                date_from=parsed_date_from,
                date_to=parsed_date_to,
            )

            orders = await order_service.search_orders(search_params)

            return SuccessResponse.create(
                data=orders, message="Order search completed successfully"
            )

        except ValueError as e:
            self.logger.warning(f"Invalid date format: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )
        except HTTPException as e:
            self.logger.warning(f"Order search failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error searching orders: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_quality_wise_summary(
        self, order_service: OrderService = Depends(get_order_service)
    ) -> APIResponse[dict]:
        """Get quality-wise beam summary for reporting"""
        try:
            self.logger.debug("Getting quality-wise beam summary")

            summary = await order_service.get_quality_wise_summary()

            return SuccessResponse.create(
                data=summary, message="Quality-wise summary generated successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Quality-wise summary generation failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error generating summary: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_orders_by_party(
        self,
        party_id: int,
        limit: Optional[int] = Query(None, description="Limit number of results"),
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[List[OrderResponse]]:
        """Get all orders for a specific party"""
        try:
            self.logger.debug(f"Getting orders for party ID: {party_id}")

            orders = await order_service.get_orders_by_party(party_id, limit)

            return SuccessResponse.create(
                data=orders, message="Party orders retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Party orders retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving party orders: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_order_statistics(
        self, order_service: OrderService = Depends(get_order_service)
    ) -> APIResponse[dict]:
        """Get order statistics for dashboard"""
        try:
            self.logger.debug("Getting order statistics")

            stats = await order_service.get_order_statistics()

            return SuccessResponse.create(
                data=stats, message="Order statistics retrieved successfully"
            )

        except HTTPException as e:
            self.logger.warning(f"Order statistics retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving order statistics: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def validate_order_data(
        self,
        order_data: dict,
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[dict]:
        """Validate order data for frontend"""
        try:
            self.logger.debug("Validating order data")

            validation_result = await order_service.validate_order_data(order_data)

            return SuccessResponse.create(
                data=validation_result, message="Order data validation completed"
            )

        except Exception as e:
            self.logger.error(f"Unexpected error validating order data: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_order_calculation_details(
        self,
        order_id: int,
        order_service: OrderService = Depends(get_order_service),
    ) -> APIResponse[List[dict]]:
        """Get detailed calculation breakdown for an order"""
        try:
            self.logger.debug(f"Getting calculation details for order: {order_id}")

            calculation_details = await order_service.get_order_calculation_details(
                order_id
            )

            return SuccessResponse.create(
                data=calculation_details,
                message="Order calculation details retrieved successfully",
            )

        except HTTPException as e:
            self.logger.warning(f"Calculation details retrieval failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error retrieving calculation details: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="Internal server error")
