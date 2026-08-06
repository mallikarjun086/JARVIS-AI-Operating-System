"""
Structlog JSON Logger setup for backend services.
"""

import logging
import sys
import structlog
from app.config import settings


def setup_logging() -> None:
    """Configures structured JSON log format."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )


def get_logger(name: str = "jarvis.backend") -> structlog.BoundLogger:
    """Returns contextual bound logger."""
    return structlog.get_logger(name)


setup_logging()
logger = get_logger()
