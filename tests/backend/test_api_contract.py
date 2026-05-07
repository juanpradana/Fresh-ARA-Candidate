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

    res = client.get("/api/v1/screener?screen_date=2026-05-06")
    assert res.status_code == 200
    body = res.json()
    assert len(body["data"]) > 0


def test_meta_latest_screen_date_exists():
    res = client.get("/api/v1/meta/latest-screen-date")
    assert res.status_code == 200
    body = res.json()
    assert body["data"]["latest_screen_date"] is not None


def test_ticker_detail_and_history_exist():
    detail = client.get("/api/v1/screener/BBCA.JK?screen_date=2026-05-06")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["data"]["ticker"] == "BBCA.JK"

    history = client.get("/api/v1/screener/BBCA.JK/history?start=2026-05-01&end=2026-05-31&preset=balanced")
    assert history.status_code == 200
    history_body = history.json()
    assert isinstance(history_body["data"], list)


def test_meta_presets_returns_default_presets():
    res = client.get("/api/v1/meta/presets")
    assert res.status_code == 200
    body = res.json()
    presets = body["data"]
    names = {preset["preset_name"] for preset in presets}
    assert {"conservative", "balanced", "aggressive"}.issubset(names)


def test_analytics_distribution_returns_summary():
    res = client.get("/api/v1/analytics/distribution?screen_date=2026-05-06&preset=balanced")
    assert res.status_code == 200
    body = res.json()
    assert "by_category" in body["data"]
    assert "by_pass_count" in body["data"]


def test_analytics_backtest_returns_summary():
    res = client.get("/api/v1/analytics/backtest?start=2026-05-01&end=2026-05-31&preset=balanced")
    assert res.status_code == 200
    body = res.json()
    assert "win_rate" in body["data"]
    assert "avg_score" in body["data"]
    assert "total" in body["data"]


def test_export_screener_csv_returns_file_content():
    res = client.get("/api/v1/export/screener.csv?screen_date=2026-05-06&preset=balanced")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "ticker" in res.text
    assert "screen_date" in res.text


def test_meta_job_runs_returns_recent_runs():
    monkeypatch_argv = [
        "cli",
        "run-daily",
        "--date",
        "2026-05-07",
    ]
    import sys

    sys.argv = monkeypatch_argv
    cli_main()

    res = client.get("/api/v1/meta/job-runs?limit=5")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1
    assert "run_date" in body["data"][0]
    assert "status" in body["data"][0]
