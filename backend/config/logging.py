"""
Logging configuration
Layer 5: Cross-Cutting Concerns
"""

import logging
import logging.config
from datetime import datetime
from pathlib import Path

from config.settings import get_settings


def setup_logging():
    """Setup application logging configuration"""
    settings = get_settings()

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = f"textile_system_{timestamp}.log"
    log_filepath = log_dir / log_filename

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG" if settings.debug else "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": str(log_filepath),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": str(log_dir / f"error_{timestamp}.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            # Root logger
            "": {
                "level": settings.log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            # Application loggers
            "textile_system": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "controllers": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "services": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "repositories": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            # Third-party loggers
            "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False,
            },
            "supabase": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

    # Apply logging configuration
    logging.config.dictConfig(logging_config)

    # Get logger for this module
    logger = logging.getLogger("textile_system.config")
    logger.info(f"Logging configured successfully. Log file: {log_filepath}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a specific module"""
    return logging.getLogger(f"textile_system.{name}")


# Request logging middleware helper
def log_request(request, response, process_time: float):
    """Log HTTP request details"""
    logger = get_logger("access")
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )


# Error logging helper
def log_error(error: Exception, context: str = "", extra_data: dict = None):
    """Log error with context and additional data"""
    logger = get_logger("error")

    error_msg = f"Error in {context}: {str(error)}"

    if extra_data:
        error_msg += f" - Extra data: {extra_data}"

    logger.error(error_msg, exc_info=True)
