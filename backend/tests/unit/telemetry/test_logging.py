"""Tests for structlog configuration."""


class TestConfigureLogging:
    """configure_logging sets up structlog without raising."""

    def test_configure_runs_without_error(self) -> None:
        from app.core.telemetry.logging import configure_logging

        configure_logging()

    def test_logger_emits_without_error(self) -> None:
        import structlog

        from app.core.telemetry.logging import configure_logging

        configure_logging()
        log = structlog.get_logger("test")
        log.info("test_event", key="value")

    def test_json_renderer_in_production(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setenv("ENVIRONMENT", "prod")
        from app.core.telemetry.logging import configure_logging

        configure_logging()

    def test_console_renderer_in_dev(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setenv("ENVIRONMENT", "dev")
        from app.core.telemetry.logging import configure_logging

        configure_logging()
