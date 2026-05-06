from app.backend.cli.commands.run_daily import should_skip_run
from app.backend.cli.main import main as cli_main
from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_screener_rows


def test_should_skip_when_job_already_successful():
    assert should_skip_run("2026-05-06", ["2026-05-06"]) is True


def test_run_daily_writes_screener_result(monkeypatch):
    init_db()

    def fake_history(_: str, __: str) -> list[dict]:
        return [
            {
                "ticker": "BBCA.JK",
                "open": 9000.0,
                "high": 9100.0,
                "low": 8950.0,
                "close": 9050.0,
                "volume": 1000000.0,
                "prev_volume": 980000.0,
                "prev_close": 9000.0,
            }
        ]

    monkeypatch.setattr("app.backend.services.market_data.service.fetch_daily_market_data", fake_history)
    monkeypatch.setattr("sys.argv", [
        "cli",
        "run-daily",
        "--date",
        "2026-05-07",
    ])

    cli_main()

    rows = get_screener_rows(screen_date="2026-05-07", preset="balanced")
    assert len(rows) >= 1
    assert rows[0]["ticker"] == "BBCA.JK"
