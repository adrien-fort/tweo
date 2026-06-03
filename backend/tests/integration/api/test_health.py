"""Integration tests for health and readiness probe endpoints."""

import os

import pytest
from fastapi.testclient import TestClient

# Disable OTel in tests to avoid collector connection noise
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("DATABASE_ENCRYPTION_KEY", "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleXRlc3Q=")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Return a TestClient backed by an in-memory SQLite database."""
    from app.main import create_app

    application = create_app()
    return TestClient(application)


class TestHealthEndpoint:
    """/health liveness probe."""

    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_healthy_status_body(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}


class TestReadyEndpoint:
    """/ready readiness probe."""

    def test_returns_200_when_db_reachable(self, client: TestClient) -> None:
        response = client.get("/ready")
        assert response.status_code == 200

    def test_returns_ready_status(self, client: TestClient) -> None:
        response = client.get("/ready")
        assert response.json() == {"status": "ready"}


class TestRequestIDMiddleware:
    """X-Request-ID header propagation."""

    def test_response_includes_request_id(self, client: TestClient) -> None:
        response = client.get("/health")
        assert "x-request-id" in response.headers

    def test_custom_request_id_echoed_back(self, client: TestClient) -> None:
        response = client.get("/health", headers={"X-Request-ID": "test-123"})
        assert response.headers["x-request-id"] == "test-123"


class TestV1PingEndpoint:
    """/api/v1/ping sanity check."""

    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/ping")
        assert response.status_code == 200

    def test_returns_pong(self, client: TestClient) -> None:
        response = client.get("/api/v1/ping")
        assert response.json() == {"message": "pong"}
