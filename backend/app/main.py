"""TWEO FastAPI application factory.

Entry point for uvicorn::

    uvicorn app.main:app --reload

Environment variables consumed at startup:

- ``DATABASE_URL``              — SQLAlchemy connection string
- ``DATABASE_ENCRYPTION_KEY``   — Fernet key for PII field encryption
- ``ENVIRONMENT``               — ``dev`` / ``staging`` / ``prod``
- ``LOG_LEVEL``                 — minimum log level (default: ``INFO``)
- ``OTEL_SDK_DISABLED``         — set to ``true`` to disable OTel entirely
- ``OTEL_EXPORTER_OTLP_ENDPOINT`` — OTel Collector base URL
"""

import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1.router import router as v1_router
from app.core.telemetry.logging import configure_logging
from app.infrastructure.persistence.database import get_engine, get_session

configure_logging()
log = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request and response.

    Reads ``X-Request-ID`` from the incoming headers if present,
    otherwise generates a new UUID. The value is bound to the structlog
    context for the duration of the request so every log line emitted
    during handling carries ``request_id``.

    The same ID is echoed back in the ``X-Request-ID`` response header
    so clients and load balancers can correlate requests to logs.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Process the request with an injected request ID."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A fully configured :class:`fastapi.FastAPI` instance with
        middleware, routers, and OpenTelemetry instrumentation applied.
    """
    app = FastAPI(
        title="TWEO API",
        description="Group activity organiser — vote on movies, games, and more.",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(RequestIDMiddleware)

    # ── Health probes (outside versioned prefix, no auth) ─────────────────────

    @app.get("/health", tags=["ops"], summary="Liveness probe")
    async def health() -> dict[str, str]:
        """Return 200 when the process is running.

        Used by Kubernetes liveness probes. Does not check dependencies.
        """
        return {"status": "healthy"}

    @app.get("/ready", tags=["ops"], summary="Readiness probe")
    async def ready() -> JSONResponse:
        """Return 200 when the application is ready to serve traffic.

        Checks that the database is reachable. Used by Kubernetes
        readiness probes — the pod is removed from the load balancer
        while this returns non-200.
        """
        try:
            with get_session() as session:
                session.execute(text("SELECT 1"))
            return JSONResponse(content={"status": "ready"})
        except Exception:
            log.error("readiness_check_failed")
            return JSONResponse(status_code=503, content={"status": "unavailable"})

    # ── Versioned API ──────────────────────────────────────────────────────────

    app.include_router(v1_router, prefix="/api/v1")

    # ── OpenTelemetry (must be last — instruments the fully configured app) ────

    from app.core.telemetry.setup import setup_telemetry

    setup_telemetry(app, get_engine())
    log.info("application_started", environment=__import__("os").environ.get("ENVIRONMENT", "dev"))

    return app


app = create_app()
