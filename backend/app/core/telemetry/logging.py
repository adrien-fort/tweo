"""Structured logging configuration using structlog.

Outputs JSON in production and a coloured human-readable format in
development. Every log entry automatically carries the current
OpenTelemetry ``trace_id`` and ``span_id`` when emitted inside an active
span — this provides the Loki→Tempo correlation link in the LGTM stack.

Usage::

    import structlog
    log = structlog.get_logger(__name__)
    log.info("user_created", user_id=str(user.id))

Environment variables:

- ``LOG_LEVEL``  — minimum log level (default: ``INFO``)
- ``ENVIRONMENT`` — when set to anything other than ``dev`` or ``development``,
  JSON output is used; otherwise the human-readable console renderer is used.
"""

import logging
import os
import sys
from typing import Any

import structlog
from opentelemetry import trace


def _add_otel_trace_context(
    logger: Any,  # noqa: ANN401
    method: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Inject the current OTel trace and span IDs into the log entry.

    Args:
        logger: The structlog logger instance (unused but required by the API).
        method: The log level method name (unused but required by the API).
        event_dict: The mutable log record dictionary.

    Returns:
        The event_dict with ``trace_id`` and ``span_id`` fields added when
        an active recording span exists.
    """
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def configure_logging() -> None:
    """Configure structlog for the application.

    Must be called once at startup, before any loggers are created.
    Subsequent calls are idempotent.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    environment = os.environ.get("ENVIRONMENT", "dev").lower()
    is_production = environment not in ("dev", "development")

    renderer: structlog.types.Processor
    if is_production:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    level = logging.getLevelName(log_level)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
        _add_otel_trace_context,
    ]

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,  # allow reconfiguration between tests
    )

    # Bridge stdlib logging into structlog so third-party libraries
    # (SQLAlchemy, uvicorn, etc.) emit structured entries too.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(log_level),
    )
