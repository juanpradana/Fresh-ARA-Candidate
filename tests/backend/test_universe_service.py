from app.backend.services.universe.service import resolve_ticker_universe


class _FakeSearch:
    def __init__(self, quotes):
        self.quotes = quotes


def test_resolve_ticker_universe_external_live_sanitizes_and_dedupes(monkeypatch):
    monkeypatch.setattr(
        "app.backend.services.universe.service.yf.Search",
        lambda **kwargs: _FakeSearch(
            [
                {"symbol": "bbca.jk"},
                {"symbol": "BBCA.JK"},
                {"symbol": "bbri"},
                {"symbol": ""},
                {"symbol": "TLKM.JK"},
            ]
        ),
        raising=False,
    )

    result = resolve_ticker_universe(mode="external_live")

    assert result["source"] == "external_live"
    assert result["fallback_used"] is False
    assert result["tickers"] == ["BBCA.JK", "BBRI.JK", "TLKM.JK"]


def test_resolve_ticker_universe_external_live_falls_back_when_empty(monkeypatch):
    monkeypatch.setattr(
        "app.backend.services.universe.service.yf.Search",
        lambda **kwargs: _FakeSearch([]),
        raising=False,
    )

    result = resolve_ticker_universe(mode="external_live")

    assert result["fallback_used"] is True
    assert result["source"] == "default_idx_fallback"
    assert result["tickers"] == ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]
