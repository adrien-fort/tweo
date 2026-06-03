"""OpenTelemetry GenAI semantic convention helpers.

Provides a context manager that creates a span conforming to the
`OpenTelemetry GenAI semantic conventions
<https://opentelemetry.io/docs/specs/semconv/gen-ai/>`_ and records
token usage metrics via :mod:`app.core.telemetry.metrics`.

Usage::

    from app.core.telemetry.ai_spans import gen_ai_span

    with gen_ai_span(
        operation="recommend_activity",
        system="anthropic",
        model="claude-sonnet-4-6",
    ) as span:
        response = call_ai_api(...)
        span.record_usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
        )

The helper is intentionally thin — it does not import any AI SDK and
works with any provider by accepting standard attribute values.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.trace import SpanKind

from app.core.telemetry.metrics import gen_ai_token_usage


class GenAISpan:
    """Wraps an active OTel span with GenAI-specific recording helpers.

    Do not instantiate directly — use :func:`gen_ai_span`.

    Attributes:
        _span: The underlying OTel span.
        _system: The GenAI system identifier (e.g. ``"anthropic"``).
        _model: The model name (e.g. ``"claude-sonnet-4-6"``).
    """

    def __init__(self, span: trace.Span, system: str, model: str) -> None:
        self._span = span
        self._system = system
        self._model = model

    def record_usage(
        self,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        finish_reason: str | None = None,
    ) -> None:
        """Record token usage and finish reason on the span and metrics.

        Args:
            input_tokens: Number of tokens in the prompt / input.
            output_tokens: Number of tokens in the completion / output.
            finish_reason: Why the model stopped (e.g. ``"end_turn"``,
                ``"max_tokens"``).
        """
        attrs = {"gen_ai.system": self._system, "gen_ai.request.model": self._model}

        if input_tokens is not None:
            self._span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
            gen_ai_token_usage.add(input_tokens, {**attrs, "token.type": "input"})

        if output_tokens is not None:
            self._span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
            gen_ai_token_usage.add(output_tokens, {**attrs, "token.type": "output"})

        if finish_reason is not None:
            self._span.set_attribute("gen_ai.response.finish_reason", finish_reason)

    def set_error(self, error_type: str) -> None:
        """Mark the span as errored with a GenAI error type attribute.

        Args:
            error_type: A short error category (e.g. ``"rate_limit"``,
                ``"context_length_exceeded"``).
        """
        self._span.set_attribute("error.type", error_type)
        self._span.set_status(trace.StatusCode.ERROR, error_type)


@contextmanager
def gen_ai_span(
    operation: str,
    system: str,
    model: str,
) -> Generator[GenAISpan, None, None]:
    """Context manager that creates a GenAI-annotated OTel span.

    Sets standard GenAI semantic convention attributes on entry and
    marks the span as an outbound client call (``SpanKind.CLIENT``).

    Args:
        operation: A short description of the operation being performed
            (e.g. ``"recommend_activity"``, ``"summarise_synopsis"``).
            Used as the span name suffix.
        system: The GenAI system identifier as defined by the OTel
            semantic conventions (e.g. ``"anthropic"``, ``"openai"``).
        model: The specific model name (e.g. ``"claude-sonnet-4-6"``).

    Yields:
        A :class:`GenAISpan` instance for recording usage and errors.

    Example:
        >>> with gen_ai_span("summarise", "anthropic", "claude-sonnet-4-6") as s:
        ...     s.record_usage(input_tokens=100, output_tokens=50)
    """
    # Tracer is resolved lazily so tests can install a custom TracerProvider
    # before the first span is created without importing concerns.
    tracer = trace.get_tracer("tweo.ai", instrumenting_library_version="0.1.0")
    span_name = f"gen_ai {operation}"
    with tracer.start_as_current_span(span_name, kind=SpanKind.CLIENT) as span:
        span.set_attribute("gen_ai.system", system)
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.operation.name", operation)
        yield GenAISpan(span, system, model)
