from fastapi.testclient import TestClient

from app.backend.api.app import app
from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import create_kpi_daily_snapshot

client = TestClient(app)


def test_create_kpi_daily_snapshot_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "kpi.sqlite"))
    init_db()

    first = create_kpi_daily_snapshot(
        run_date="2026-05-18",
        preset="balanced",
        precision_at_top_n=0.75,
        screener_views=12,
        alerts_views=3,
        watchlist_views=5,
    )
    second = create_kpi_daily_snapshot(
        run_date="2026-05-18",
        preset="balanced",
        precision_at_top_n=0.80,
        screener_views=100,
        alerts_views=50,
        watchlist_views=20,
    )

    assert first is True
    assert second is False

    res = client.get("/api/v1/analytics/kpi?start=2026-05-18&end=2026-05-18&preset=balanced")
    assert res.status_code == 200
    body = res.json()
    assert body["data"]["total_days"] == 1
    assert body["data"]["avg_precision_at_top_n"] == 0.75
    assert body["data"]["total_screener_views"] == 12
    assert body["data"]["total_alerts_views"] == 3
    assert body["data"]["total_watchlist_views"] == 5


def test_kpi_endpoint_aggregates_multiple_days(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "kpi.sqlite"))
    init_db()

    create_kpi_daily_snapshot(
        run_date="2026-05-19",
        preset="balanced",
        precision_at_top_n=0.6,
        screener_views=10,
        alerts_views=1,
        watchlist_views=2,
    )
    create_kpi_daily_snapshot(
        run_date="2026-05-20",
        preset="balanced",
        precision_at_top_n=0.9,
        screener_views=8,
        alerts_views=2,
        watchlist_views=3,
    )

    res = client.get("/api/v1/analytics/kpi?start=2026-05-19&end=2026-05-20&preset=balanced")
    assert res.status_code == 200
    body = res.json()
    assert body["meta"]["start"] == "2026-05-19"
    assert body["meta"]["end"] == "2026-05-20"
    assert body["meta"]["preset"] == "balanced"
    assert body["data"]["total_days"] == 2
    assert body["data"]["avg_precision_at_top_n"] == 0.75
    assert body["data"]["total_screener_views"] == 18
    assert body["data"]["total_alerts_views"] == 3
    assert body["data"]["total_watchlist_views"] == 5
