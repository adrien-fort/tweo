"""Tests for GenAI semantic convention span helpers."""

import opentelemetry.trace as trace_api
import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


@pytest.fixture
def otel_exporter() -> InMemorySpanExporter:
    """Provide an InMemorySpanExporter wired as the global TracerProvider.

    The OTel SDK uses a ``Once`` guard (``_TRACER_PROVIDER_SET_ONCE``) that
    prevents the global provider from being replaced after the first
    ``set_tracer_provider`` call. Both the provider reference and the
    guard must be reset for each test to get a clean in-memory provider.

    ``OTEL_SDK_DISABLED=true`` causes the SDK ``TracerProvider`` to return a
    ``NoOpTracer`` regardless of which provider is installed. That env var may
    be set by the integration test suite to suppress collector noise, so it
    must be removed for the duration of each span test.
    """
    import os

    # Save state
    old_provider = trace_api._TRACER_PROVIDER  # type: ignore[attr-defined]
    old_once = trace_api._TRACER_PROVIDER_SET_ONCE  # type: ignore[attr-defined]
    old_sdk_disabled = os.environ.pop("OTEL_SDK_DISABLED", None)

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    # Reset both guards so set_tracer_provider is accepted
    trace_api._TRACER_PROVIDER = None  # type: ignore[attr-defined]
    trace_api._TRACER_PROVIDER_SET_ONCE = trace_api.Once()  # type: ignore[attr-defined]
    trace.set_tracer_provider(provider)

    yield exporter

    exporter.clear()
    trace_api._TRACER_PROVIDER = old_provider  # type: ignore[attr-defined]
    trace_api._TRACER_PROVIDER_SET_ONCE = old_once  # type: ignore[attr-defined]
    if old_sdk_disabled is not None:
        os.environ["OTEL_SDK_DISABLED"] = old_sdk_disabled


class TestGenAISpan:
    """gen_ai_span sets correct GenAI semantic convention attributes."""

    def test_span_name_includes_operation(self, otel_exporter: InMemorySpanExporter) -> None:
        from app.core.telemetry.ai_spans import gen_ai_span

        with gen_ai_span("recommend_activity", "anthropic", "claude-sonnet-4-6"):
            pass  # no body needed; we only inspect the finished span below

        spans = otel_exporter.get_finished_spans()
        assert len(spans) == 1
        assert "recommend_activity" in spans[0].name

    def test_gen_ai_system_and_model_set(self, otel_exporter: InMemorySpanExporter) -> None:
        from app.core.telemetry.ai_spans import gen_ai_span

        with gen_ai_span("summarise", "openai", "gpt-4o"):
            pass  # no body needed; attributes are set on entry and span closes on exit

        span = otel_exporter.get_finished_spans()[0]
        assert span.attributes["gen_ai.system"] == "openai"
        assert span.attributes["gen_ai.request.model"] == "gpt-4o"
        assert span.attributes["gen_ai.operation.name"] == "summarise"

    def test_record_usage_sets_token_attributes(self, otel_exporter: InMemorySpanExporter) -> None:
        from app.core.telemetry.ai_spans import gen_ai_span

        with gen_ai_span("recommend", "anthropic", "claude-haiku-4-5") as s:
            s.record_usage(input_tokens=120, output_tokens=45, finish_reason="end_turn")

        span = otel_exporter.get_finished_spans()[0]
        assert span.attributes["gen_ai.usage.input_tokens"] == 120
        assert span.attributes["gen_ai.usage.output_tokens"] == 45
        assert span.attributes["gen_ai.response.finish_reason"] == "end_turn"

    def test_record_usage_partial_tokens(self, otel_exporter: InMemorySpanExporter) -> None:
        from app.core.telemetry.ai_spans import gen_ai_span

        with gen_ai_span("op", "anthropic", "claude-sonnet-4-6") as s:
            s.record_usage(input_tokens=50)

        span = otel_exporter.get_finished_spans()[0]
        assert span.attributes["gen_ai.usage.input_tokens"] == 50
        assert "gen_ai.usage.output_tokens" not in span.attributes

    def test_set_error_marks_span_errored(self, otel_exporter: InMemorySpanExporter) -> None:
        from app.core.telemetry.ai_spans import gen_ai_span

        with gen_ai_span("op", "anthropic", "claude-sonnet-4-6") as s:
            s.set_error("rate_limit")

        span = otel_exporter.get_finished_spans()[0]
        assert span.attributes["error.type"] == "rate_limit"
        assert span.status.status_code == trace.StatusCode.ERROR

    def test_span_kind_is_client(self, otel_exporter: InMemorySpanExporter) -> None:
        from opentelemetry.trace import SpanKind

        from app.core.telemetry.ai_spans import gen_ai_span

        with gen_ai_span("op", "anthropic", "claude-sonnet-4-6"):
            pass  # no body needed; kind is set at span creation

        span = otel_exporter.get_finished_spans()[0]
        assert span.kind == SpanKind.CLIENT
