import pytest
from fastapi.testclient import TestClient

from api.main import app, servers


@pytest.fixture(autouse=True)
def reset_store():
    servers.clear()
    yield
    servers.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_returns_cpu_percent(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "cpu_percent" in response.json()


def test_post_servers_without_api_key_returns_403(client):
    response = client.post(
        "/servers",
        json={"name": "api-prod", "host": "127.0.0.1", "port": 8000},
    )

    assert response.status_code == 403


def test_post_servers_with_valid_api_key_creates_server(client):
    response = client.post(
        "/servers",
        headers={"X-API-Key": "demo-key"},
        json={"name": "api-prod", "host": "127.0.0.1", "port": 8000},
    )

    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "api-prod"
    assert created["status"] == "unknown"

    list_response = client.get("/servers")
    assert list_response.status_code == 200
    assert created in list_response.json()


def test_get_nonexistent_server_returns_404(client):
    response = client.get("/servers/999")

    assert response.status_code == 404
