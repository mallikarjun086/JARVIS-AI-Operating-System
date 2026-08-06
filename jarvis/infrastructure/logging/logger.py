"""
Structured Logging Infrastructure using Structlog.
Provides JSON output formatting and contextual binding for telemetry tracking.
"""

import logging
import sys
import structlog
from jarvis.config import settings


def configure_logger() -> None:
    """Configures global structlog logging settings."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "jarvis") -> structlog.BoundLogger:
    """Returns a contextual bound logger instance."""
    return structlog.get_logger(name)


# Initialize logger configuration on module load
configure_logger()
logger = get_logger()
