from app.backend.services.universe.service import get_external_live_idx_universe, resolve_ticker_universe


class _FakeLookup:
    def __init__(self, rows):
        self._rows = rows

    def get_stock(self, count=250):
        return self._rows


class _FakeFrame:
    def __init__(self, rows):
        self._rows = rows
        self.empty = len(rows) == 0

    def iterrows(self):
        for symbol, data in self._rows:
            yield symbol, data


def test_get_external_live_idx_universe_filters_jkt_equity_and_dedupes(monkeypatch):
    rows = _FakeFrame(
        [
            ("BBCA.JK", {"exchange": "JKT", "quoteType": "equity"}),
            ("bbca.jk", {"exchange": "JKT", "quoteType": "equity"}),
            ("BBRI.JK", {"exchange": "JKT", "quoteType": "equity"}),
            ("JKIL.NS", {"exchange": "NSI", "quoteType": "equity"}),
            ("0P0000K0KF", {"exchange": "PNK", "quoteType": "mutualfund"}),
            ("ASII", {"exchange": "OID", "quoteType": "equity"}),
            ("TLKM.JK", {"exchange": "JKT", "quoteType": "equity"}),
        ]
    )
    monkeypatch.setattr(
        "app.backend.services.universe.service.yf.Lookup",
        lambda query, raise_errors=False: _FakeLookup(rows),
        raising=False,
    )

    tickers = get_external_live_idx_universe(max_results=250)

    assert tickers == ["BBCA.JK", "BBRI.JK", "TLKM.JK"]


def test_resolve_ticker_universe_external_live_falls_back_when_empty(monkeypatch):
    empty = _FakeFrame([])
    monkeypatch.setattr(
        "app.backend.services.universe.service.yf.Lookup",
        lambda query, raise_errors=False: _FakeLookup(empty),
        raising=False,
    )

    result = resolve_ticker_universe(mode="external_live")

    assert result["fallback_used"] is True
    assert result["source"] == "default_idx_fallback"
    assert result["tickers"] == ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]
