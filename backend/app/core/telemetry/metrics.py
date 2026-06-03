"""Custom OpenTelemetry application metrics.

All meters use the ``tweo.`` namespace. Instruments are module-level
singletons — import and call them directly from service or handler code::

    from app.core.telemetry.metrics import events_created
    events_created.add(1, {"activity_type": event.activity_type.value})

Metrics are exported to the configured OTel Collector and surface in
Grafana via Mimir (production) or the console exporter (development).
"""

from opentelemetry import metrics

_meter = metrics.get_meter("tweo.app", version="0.1.0")

# ── Event metrics ─────────────────────────────────────────────────────────────

events_created = _meter.create_counter(
    name="tweo.events.created",
    description="Total number of events created.",
    unit="1",
)
"""Increment when an event is successfully created.

Recommended attributes: ``activity_type``, ``privacy``.
"""

# ── Voting metrics ────────────────────────────────────────────────────────────

votes_cast = _meter.create_counter(
    name="tweo.votes.cast",
    description="Total number of votes cast across all events.",
    unit="1",
)
"""Increment when a user casts a vote.

Recommended attributes: ``activity_type``.
"""

active_voting_sessions = _meter.create_up_down_counter(
    name="tweo.voting_sessions.active",
    description="Number of events currently in VOTING status.",
    unit="1",
)
"""Increment when an event transitions to VOTING; decrement when it leaves."""

# ── User metrics ──────────────────────────────────────────────────────────────

users_registered = _meter.create_counter(
    name="tweo.users.registered",
    description="Total number of user accounts created.",
    unit="1",
)
"""Increment when a new user completes registration."""

# ── AI metrics (GenAI semantic conventions) ───────────────────────────────────

gen_ai_token_usage = _meter.create_counter(
    name="tweo.gen_ai.tokens",
    description="Total tokens consumed by GenAI calls.",
    unit="1",
)
"""Increment with token counts from AI calls.

Recommended attributes: ``gen_ai.system``, ``gen_ai.request.model``,
``token.type`` (``input`` or ``output``).

Example::

    gen_ai_token_usage.add(prompt_tokens, {
        "gen_ai.system": "anthropic",
        "gen_ai.request.model": "claude-sonnet-4-6",
        "token.type": "input",
    })
"""
