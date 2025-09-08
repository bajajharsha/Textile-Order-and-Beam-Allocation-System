"""
Health check API routes
Layer 1: Presentation Layer - Route Definitions
"""

from datetime import datetime

from config.database import check_db_health
from config.logging import get_logger
from config.settings import get_settings
from fastapi import APIRouter
from models.base import APIResponse, SuccessResponse

# Create router instance
router = APIRouter(prefix="/health", tags=["health"])

# Initialize logger
logger = get_logger("routes.health")


# Routes
@router.get(
    "/",
    response_model=APIResponse[dict],
    summary="Basic health check",
    description="Basic application health status",
)
async def health_check():
    """Basic health check endpoint"""
    try:
        settings = get_settings()

        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

        return SuccessResponse.create(
            data=health_data, message="Application is healthy"
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": "Health check failed",
            "error": str(e),
        }


@router.get(
    "/detailed",
    response_model=APIResponse[dict],
    summary="Detailed health check",
    description="Detailed application health including database connectivity",
)
async def detailed_health_check():
    """Detailed health check including database connectivity"""
    try:
        settings = get_settings()

        # Get database health
        db_health = await check_db_health()

        # Calculate uptime (simple version)
        import psutil

        boot_time = psutil.boot_time()
        current_time = datetime.now().timestamp()
        uptime_seconds = current_time - boot_time

        health_data = {
            "status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "application": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
                "debug": settings.debug,
            },
            "database": db_health,
            "uptime_seconds": uptime_seconds,
            "authentication_enabled": settings.enable_authentication,
        }

        message = "All systems operational"
        if db_health["status"] != "healthy":
            message = "Application running with degraded database connectivity"

        return SuccessResponse.create(data=health_data, message=message)

    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": "Detailed health check failed",
            "error": str(e),
        }


@router.get(
    "/database",
    response_model=APIResponse[dict],
    summary="Database health check",
    description="Check database connectivity and status",
)
async def database_health_check():
    """Database-specific health check"""
    try:
        db_health = await check_db_health()

        message = (
            "Database is healthy"
            if db_health["status"] == "healthy"
            else "Database connectivity issues"
        )

        return SuccessResponse.create(data=db_health, message=message)

    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": "Database health check failed",
            "error": str(e),
        }
