from fastapi.testclient import TestClient

from app.backend.api.app import app
from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import (
    add_watchlist_ticker,
    list_alert_events,
    upsert_feature_daily,
    upsert_screening_result,
)
from app.backend.services.alerts.service import capture_watchlist_alerts

client = TestClient(app)


def test_capture_watchlist_alerts_creates_event_for_watchlist_match(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "alerts.sqlite"))
    init_db()

    add_watchlist_ticker("default", "BBCA.JK")
    upsert_feature_daily(
        trade_date="2026-05-15",
        ticker="BBCA.JK",
        vol_ratio=1.0,
        range_pct=0.8,
        price_action=0.6,
        is_ara_t0=0,
        feature_version="v1",
    )
    upsert_screening_result(
        screen_date="2026-05-15",
        feature_date="2026-05-15",
        ticker="BBCA.JK",
        preset_name="balanced",
        score=0.9,
        pass_vol_ratio=1,
        pass_range_pct=1,
        pass_price_action=1,
        pass_is_ara_t0=1,
        pass_count=4,
        category="ideal",
        reason_json=None,
    )

    inserted = capture_watchlist_alerts("2026-05-15", "balanced")

    assert inserted == 1
    events = list_alert_events(limit=10)
    assert len(events) == 1
    assert events[0]["run_date"] == "2026-05-15"
    assert events[0]["watchlist_name"] == "default"
    assert events[0]["ticker"] == "BBCA.JK"
    assert events[0]["preset"] == "balanced"


def test_capture_watchlist_alerts_is_idempotent_for_same_run(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "alerts.sqlite"))
    init_db()

    add_watchlist_ticker("swing", "ASII.JK")
    upsert_feature_daily(
        trade_date="2026-05-16",
        ticker="ASII.JK",
        vol_ratio=1.0,
        range_pct=0.7,
        price_action=0.5,
        is_ara_t0=0,
        feature_version="v1",
    )
    upsert_screening_result(
        screen_date="2026-05-16",
        feature_date="2026-05-16",
        ticker="ASII.JK",
        preset_name="balanced",
        score=0.88,
        pass_vol_ratio=1,
        pass_range_pct=1,
        pass_price_action=1,
        pass_is_ara_t0=1,
        pass_count=4,
        category="ideal",
        reason_json=None,
    )

    first = capture_watchlist_alerts("2026-05-16", "balanced")
    second = capture_watchlist_alerts("2026-05-16", "balanced")

    assert first == 1
    assert second == 0
    events = list_alert_events(limit=10)
    assert len(events) == 1


def test_alerts_api_returns_recent_events(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "alerts.sqlite"))
    init_db()

    add_watchlist_ticker("default", "TLKM.JK")
    upsert_feature_daily(
        trade_date="2026-05-17",
        ticker="TLKM.JK",
        vol_ratio=1.0,
        range_pct=0.7,
        price_action=0.6,
        is_ara_t0=0,
        feature_version="v1",
    )
    upsert_screening_result(
        screen_date="2026-05-17",
        feature_date="2026-05-17",
        ticker="TLKM.JK",
        preset_name="balanced",
        score=0.86,
        pass_vol_ratio=1,
        pass_range_pct=1,
        pass_price_action=1,
        pass_is_ara_t0=1,
        pass_count=4,
        category="ideal",
        reason_json=None,
    )
    capture_watchlist_alerts("2026-05-17", "balanced")

    res = client.get("/api/v1/alerts/recent?limit=5")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 1
    assert body["data"][0]["ticker"] == "TLKM.JK"
    assert body["meta"]["limit"] == 5
    assert body["error"] is None
