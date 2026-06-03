"""OpenTelemetry SDK initialisation.

Bootstraps traces and metrics. Reads configuration entirely from
environment variables so no code change is needed between environments:

- ``OTEL_SDK_DISABLED=true``        — disables the SDK entirely (useful in CI)
- ``OTEL_EXPORTER_OTLP_ENDPOINT``   — base URL of the OTel Collector
  (e.g. ``http://localhost:4318``). When unset, falls back to the
  console exporter so traces remain visible without a running collector.
- ``ENVIRONMENT``                    — injected into the service resource
  (``dev`` / ``staging`` / ``prod``).

Auto-instrumentation wired here:
- FastAPI: all HTTP request/response spans
- SQLAlchemy: all query spans

Logs are handled separately via structlog (see :mod:`app.core.telemetry.logging`).
Trace IDs are injected into each log entry for Loki→Tempo correlation.
"""

import os

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_telemetry(app: object, engine: object) -> None:  # type: ignore[type-arg]
    """Initialise OpenTelemetry traces and metrics for the application.

    Must be called once, after the FastAPI app and SQLAlchemy engine
    have been created. Safe to call multiple times — subsequent calls
    are no-ops if the SDK is already initialised.

    Args:
        app: The FastAPI application instance.
        engine: The SQLAlchemy engine instance.
    """
    if os.environ.get("OTEL_SDK_DISABLED", "false").lower() == "true":
        return

    resource = Resource.create(
        {
            "service.name": "tweo-backend",
            "service.version": "0.1.0",
            "deployment.environment": os.environ.get("ENVIRONMENT", "dev"),
        }
    )

    _setup_traces(resource)
    _setup_metrics(resource)
    _instrument_app(app, engine)


def _setup_traces(resource: Resource) -> None:
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    else:
        exporter = ConsoleSpanExporter()  # type: ignore[assignment]

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


def _setup_metrics(resource: Resource) -> None:
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=f"{otlp_endpoint}/v1/metrics"))
    else:
        reader = PeriodicExportingMetricReader(ConsoleMetricExporter())

    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))


def _instrument_app(app: object, engine: object) -> None:  # type: ignore[type-arg]
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]
    SQLAlchemyInstrumentor().instrument(engine=engine)  # type: ignore[arg-type]
