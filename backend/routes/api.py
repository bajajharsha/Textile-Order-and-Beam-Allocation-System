"""
Main API router that combines all route modules
Layer 1: Presentation Layer - API Router
"""

from fastapi import APIRouter

from routes.health_routes import router as health_router
from routes.lot_routes import router as lot_router
from routes.master_routes import router as master_router
from routes.order_routes import router as order_router
from routes.party_routes import router as party_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router)
api_router.include_router(party_router)
api_router.include_router(order_router)
api_router.include_router(lot_router)
api_router.include_router(master_router)


# Add root endpoint for API information
@api_router.get("/", tags=["root"])
async def api_root():
    """API root endpoint with information"""
    return {
        "message": "Textile Order & Beam Allocation System API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "parties": "/parties",
            "orders": "/orders",
            "lots": "/lots",
            "master_data": "/master",
        },
    }
