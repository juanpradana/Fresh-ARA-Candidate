from fastapi.testclient import TestClient

from app.backend.api.app import app
from app.backend.core.db import init_db

client = TestClient(app)


def _prepare_isolated_db(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "watchlist.sqlite"))
    init_db()


def test_watchlist_starts_empty(tmp_path, monkeypatch):
    _prepare_isolated_db(tmp_path, monkeypatch)

    res = client.get("/api/v1/watchlists")
    assert res.status_code == 200
    body = res.json()
    assert body["data"] == []
    assert body["error"] is None


def test_watchlist_add_and_list_ticker(tmp_path, monkeypatch):
    _prepare_isolated_db(tmp_path, monkeypatch)

    create = client.post("/api/v1/watchlists/default/tickers", json={"ticker": "BBCA.JK"})
    assert create.status_code == 200
    create_body = create.json()
    assert create_body["data"]["watchlist_name"] == "default"
    assert create_body["data"]["ticker"] == "BBCA.JK"

    listed = client.get("/api/v1/watchlists/default/tickers")
    assert listed.status_code == 200
    listed_body = listed.json()
    assert listed_body["data"] == [{"watchlist_name": "default", "ticker": "BBCA.JK"}]


def test_watchlist_add_is_idempotent(tmp_path, monkeypatch):
    _prepare_isolated_db(tmp_path, monkeypatch)

    first = client.post("/api/v1/watchlists/default/tickers", json={"ticker": "BBRI.JK"})
    assert first.status_code == 200

    second = client.post("/api/v1/watchlists/default/tickers", json={"ticker": "BBRI.JK"})
    assert second.status_code == 200

    listed = client.get("/api/v1/watchlists/default/tickers")
    body = listed.json()
    matches = [item for item in body["data"] if item["ticker"] == "BBRI.JK"]
    assert len(matches) == 1


def test_watchlist_remove_ticker(tmp_path, monkeypatch):
    _prepare_isolated_db(tmp_path, monkeypatch)

    created = client.post("/api/v1/watchlists/default/tickers", json={"ticker": "TLKM.JK"})
    assert created.status_code == 200

    deleted = client.delete("/api/v1/watchlists/default/tickers/TLKM.JK")
    assert deleted.status_code == 200
    deleted_body = deleted.json()
    assert deleted_body["data"]["removed"] is True

    listed = client.get("/api/v1/watchlists/default/tickers")
    listed_body = listed.json()
    assert all(item["ticker"] != "TLKM.JK" for item in listed_body["data"])
