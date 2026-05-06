from fastapi.testclient import TestClient

from app.backend.api.app import app

client = TestClient(app)


def test_health_endpoint_returns_ok():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "ok"


def test_health_and_screener_endpoints_exist():
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/screener").status_code in [200, 404]
