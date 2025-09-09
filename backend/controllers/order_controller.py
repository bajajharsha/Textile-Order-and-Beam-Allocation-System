"""
Order Controller - API request handlers
"""

from fastapi import HTTPException
from usecases.order_usecase import OrderUseCase


class OrderController:
    """Order API handlers"""

    def __init__(self):
        self.use_case = OrderUseCase()

    async def create_order(self, order_data: dict) -> dict:
        """Handle create order request"""
        try:
            order = await self.use_case.create_order(order_data)
            return order.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def get_order(self, order_id: int) -> dict:
        """Handle get order request"""
        try:
            return await self.use_case.get_order(order_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def update_order(self, order_id: int, update_data: dict) -> dict:
        """Handle update order request"""
        try:
            order = await self.use_case.update_order(order_id, update_data)
            return order.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def delete_order(self, order_id: int) -> dict:
        """Handle delete order request"""
        try:
            success = await self.use_case.delete_order(order_id)
            return {"success": success, "message": "Order deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def list_orders(self, page: int = 1, page_size: int = 20) -> dict:
        """Handle list orders request"""
        try:
            return await self.use_case.list_orders(page, page_size)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def search_orders(self, query: str, limit: int = 20) -> dict:
        """Handle search orders request"""
        try:
            orders = await self.use_case.search_orders(query, limit)
            return {"orders": orders, "total": len(orders)}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    async def calculate_beam_preview(
        self, ground_colors: list, design_numbers: list, pieces_per_color: int
    ) -> dict:
        """Handle beam calculation preview request"""
        try:
            return await self.use_case.calculate_beam_preview(
                ground_colors, design_numbers, pieces_per_color
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )
