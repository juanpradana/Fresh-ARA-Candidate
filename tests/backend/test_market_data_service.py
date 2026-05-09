from app.backend.services.market_data.service import fetch_daily_market_data


class _FakeILoc:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def __getitem__(self, index: int) -> dict:
        return self._rows[index]


class _FakeHistory:
    def __init__(self, rows: list[dict]):
        self._rows = rows
        self.iloc = _FakeILoc(rows)

    @property
    def empty(self) -> bool:
        return len(self._rows) == 0

    def __len__(self) -> int:
        return len(self._rows)


class _FakeTicker:
    def __init__(self, _ticker: str, calls: list[dict[str, str | None]]):
        self._calls = calls

    def history(self, start: str | None = None, end: str | None = None, period: str | None = None):
        self._calls.append({"start": start, "end": end, "period": period})
        if period == "5d":
            return _FakeHistory([
                {"Close": 9000.0, "Volume": 980000.0},
                {"Close": 9050.0, "Volume": 1000000.0},
            ])
        return _FakeHistory([
            {
                "Open": 9000.0,
                "High": 9100.0,
                "Low": 8950.0,
                "Close": 9050.0,
                "Volume": 1000000.0,
            }
        ])


def test_fetch_daily_market_data_uses_next_day_end_window(monkeypatch):
    calls: list[dict[str, str | None]] = []

    def fake_ticker(symbol: str):
        return _FakeTicker(symbol, calls)

    monkeypatch.setattr("app.backend.services.market_data.service.yf.Ticker", fake_ticker)

    rows = fetch_daily_market_data("BBCA.JK", "2026-05-08", max_attempts=1)

    assert rows and rows[0]["ticker"] == "BBCA.JK"
    assert calls[0]["start"] == "2026-05-08"
    assert calls[0]["end"] == "2026-05-09"
