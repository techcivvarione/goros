"""Structured logging configuration for the GOROS API service."""

from __future__ import annotations

import logging
import sys
from logging.config import dictConfig

import structlog
from structlog.typing import EventDict, Processor, WrappedLogger

from app.core.config import Settings


def add_default_log_fields(
    _: WrappedLogger,
    __: str,
    event_dict: EventDict,
) -> EventDict:
    """Ensure required structured fields are always present."""

    event_dict.setdefault("request_id", None)
    event_dict.setdefault("module", None)
    event_dict.setdefault("latency", None)
    event_dict.setdefault("organization_id", None)
    event_dict.setdefault("user_id", None)
    return event_dict


def configure_logging(settings: Settings) -> None:
    """Configure standard logging and structlog processors for the process."""

    log_level = logging.DEBUG if settings.debug else logging.INFO
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        add_default_log_fields,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor
    # `computed_field` makes `is_development` a real bool property at runtime,
    # but without the pydantic mypy plugin, mypy sees the undecorated function
    # object and (incorrectly) flags it as always-truthy.
    if settings.is_development:  # type: ignore[truthy-function]
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structlog": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": renderer,
                    "foreign_pre_chain": shared_processors,
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "structlog",
                    "stream": sys.stdout,
                }
            },
            "root": {
                "handlers": ["default"],
                "level": log_level,
            },
        }
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to the provided name."""

    return structlog.get_logger(name)
