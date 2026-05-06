from fastapi.testclient import TestClient

from app.backend.api.app import app
from app.backend.cli.main import main as cli_main

client = TestClient(app)


def test_health_endpoint_returns_ok():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "ok"


def test_health_and_screener_endpoints_exist():
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/screener").status_code in [200, 404]


def test_screener_returns_data_after_run_daily(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "cli",
        "run-daily",
        "--date",
        "2026-05-06",
    ])
    cli_main()

    res = client.get("/api/v1/screener")
    assert res.status_code == 200
    body = res.json()
    assert len(body["data"]) > 0
