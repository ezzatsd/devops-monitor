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
    payload = response.json()
    assert "cpu_percent" in payload
    assert "memory_percent" in payload
    assert "disk_percent" in payload


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


def test_delete_server_with_valid_api_key(client):
    create_response = client.post(
        "/servers",
        headers={"X-API-Key": "demo-key"},
        json={"name": "api-prod", "host": "127.0.0.1", "port": 8000},
    )
    server_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/servers/{server_id}",
        headers={"X-API-Key": "demo-key"},
    )

    assert delete_response.status_code == 204
    assert client.get(f"/servers/{server_id}").status_code == 404


def test_manual_health_check_returns_server_status(client):
    create_response = client.post(
        "/servers",
        headers={"X-API-Key": "demo-key"},
        json={"name": "missing", "host": "127.0.0.1", "port": 65530},
    )
    server_id = create_response.json()["id"]

    response = client.post(f"/servers/{server_id}/check")

    assert response.status_code == 200
    assert response.json()["status"] in {"UP", "DEGRADED", "DOWN", "unknown"}


def test_get_nonexistent_server_returns_404(client):
    response = client.get("/servers/999")

    assert response.status_code == 404


def test_metrics_websocket_sends_json_frame(client):
    with client.websocket_connect("/ws/metrics") as websocket:
        payload = websocket.receive_json()

    assert "cpu_percent" in payload
    assert "memory_percent" in payload
    assert "disk_percent" in payload
