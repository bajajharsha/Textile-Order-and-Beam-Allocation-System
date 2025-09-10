"""
Textile Order and Beam Allocation System - FastAPI Backend
Main application entry point with 5-layer architecture
"""

from contextlib import asynccontextmanager

import uvicorn
from config.database import database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.master_routes import router as master_router
from routes.order_routes import router as order_router
from routes.party_routes import router as party_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    Handles startup and shutdown events
    """
    # Startup
    print("Starting Textile Order & Beam Allocation System...")
    try:
        await database.connect()
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")

    yield

    # Shutdown
    try:
        await database.disconnect()
    except Exception as e:
        print(f"Database cleanup warning: {str(e)}")


# Create FastAPI application instance
app = FastAPI(
    title="Textile Order & Beam Allocation System",
    description="A comprehensive system for managing textile orders and beam allocations",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(party_router, prefix="/api/v1/parties", tags=["parties"])
app.include_router(master_router, prefix="/api/v1/master", tags=["master-data"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["orders"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Textile Order & Beam Allocation System API",
        "version": "1.0.0",
        "status": "healthy",
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
