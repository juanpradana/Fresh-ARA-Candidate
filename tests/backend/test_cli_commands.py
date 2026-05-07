from app.backend.cli.main import main as cli_main


def test_update_market_command_dispatches(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(date: str, batch_size: int, qps: float) -> None:
        captured["date"] = date
        captured["batch_size"] = batch_size
        captured["qps"] = qps

    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "update-market", "--date", "2026-05-07", "--batch-size", "25", "--qps", "2.5"],
    )

    cli_main()

    assert captured == {
        "date": "2026-05-07",
        "batch_size": 25,
        "qps": 2.5,
    }


def test_run_screening_command_dispatches(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(date: str, preset: str) -> None:
        captured["date"] = date
        captured["preset"] = preset

    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "run-screening", "--date", "2026-05-07", "--preset", "aggressive"],
    )

    cli_main()

    assert captured == {
        "date": "2026-05-07",
        "preset": "aggressive",
    }


def test_schedule_screening_command_dispatches(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(timezone: str) -> None:
        captured["timezone"] = timezone

    monkeypatch.setattr("app.backend.cli.main.handle_schedule_screening", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "schedule-screening", "--timezone", "Asia/Jakarta"],
    )

    cli_main()

    assert captured == {
        "timezone": "Asia/Jakarta",
    }
