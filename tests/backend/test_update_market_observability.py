from app.backend.cli.commands.update_market import handle_update_market


def test_update_market_returns_observability_counters(monkeypatch):
    monkeypatch.setattr("app.backend.cli.commands.update_market.init_db", lambda: None, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.commands.update_market.get_default_idx_universe",
        lambda: ["AAA.JK", "BBB.JK", "CCC.JK"],
        raising=False,
    )
    monkeypatch.setattr(
        "app.backend.cli.commands.update_market.get_missing_tickers_for_date",
        lambda trade_date, tickers: ["AAA.JK", "BBB.JK", "CCC.JK"],
        raising=False,
    )

    def fake_fetch(ticker: str, date: str, limiter=None, breaker=None, cache=None):
        if ticker == "AAA.JK":
            return [{
                "ticker": "AAA.JK",
                "open": 1.0,
                "high": 2.0,
                "low": 0.9,
                "close": 1.5,
                "volume": 100.0,
            }]
        if ticker == "BBB.JK":
            return []
        raise RuntimeError("source down")

    writes: list[dict] = []

    def fake_upsert(**kwargs):
        writes.append(kwargs)

    monkeypatch.setattr("app.backend.cli.commands.update_market.market_data_service.fetch_daily_market_data", fake_fetch, raising=False)
    monkeypatch.setattr("app.backend.cli.commands.update_market.upsert_price_daily", fake_upsert, raising=False)

    result = handle_update_market("2026-05-07", batch_size=2, qps=2.0)

    assert result["expected"] == 3
    assert result["fetched"] == 1
    assert result["is_complete"] is False
    assert result["tickers_ok"] == 1
    assert result["tickers_empty"] == 1
    assert result["tickers_error"] == 1
    assert result["rows_upserted"] == 1
    assert result["batch_count"] == 2
    assert len(writes) == 1


def test_update_market_collects_observability_events(monkeypatch):
    monkeypatch.setattr("app.backend.cli.commands.update_market.init_db", lambda: None, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.commands.update_market.get_default_idx_universe",
        lambda: ["AAA.JK", "BBB.JK"],
        raising=False,
    )
    monkeypatch.setattr(
        "app.backend.cli.commands.update_market.get_missing_tickers_for_date",
        lambda trade_date, tickers: ["AAA.JK", "BBB.JK"],
        raising=False,
    )

    def fake_fetch(ticker: str, date: str, limiter=None, breaker=None, cache=None):
        if ticker == "AAA.JK":
            return [{
                "ticker": "AAA.JK",
                "open": 1.0,
                "high": 2.0,
                "low": 0.9,
                "close": 1.5,
                "volume": 100.0,
            }]
        return []

    monkeypatch.setattr("app.backend.cli.commands.update_market.market_data_service.fetch_daily_market_data", fake_fetch, raising=False)
    monkeypatch.setattr("app.backend.cli.commands.update_market.upsert_price_daily", lambda **_: None, raising=False)

    events: list[dict[str, object]] = []
    result = handle_update_market("2026-05-07", batch_size=50, qps=2.0, on_event=events.append)

    assert result["tickers_ok"] == 1
    assert result["tickers_empty"] == 1
    assert [event["event"] for event in events if event["event"] == "update_market.ticker_outcome"] == [
        "update_market.ticker_outcome",
        "update_market.ticker_outcome",
    ]
    completed = [event for event in events if event["event"] == "update_market.run_completed"]
    assert len(completed) == 1
    assert completed[0]["expected"] == 2
    assert completed[0]["fetched"] == 1
    assert completed[0]["batch_count"] == 1
