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


def test_run_daily_orchestrates_pipeline_handlers(monkeypatch):
    calls: list[str] = []

    def fake_update(date: str, batch_size: int, qps: float) -> None:
        calls.append(f"update:{date}:{batch_size}:{qps}")

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append(f"compute:{date}:{feature_version}")

    def fake_screen(date: str, preset: str) -> None:
        calls.append(f"screen:{date}:{preset}")

    def fail_legacy(_: str, batch_size: int = 50) -> None:
        raise AssertionError(f"legacy run_daily_job should not be called ({batch_size})")

    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("app.backend.cli.main.run_daily_job", fail_legacy, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "run-daily",
            "--date",
            "2026-05-07",
            "--preset",
            "aggressive",
            "--batch-size",
            "25",
            "--qps",
            "3",
        ],
    )

    cli_main()

    assert calls == [
        "update:2026-05-07:25:3.0",
        "compute:2026-05-07:v1",
        "screen:2026-05-07:aggressive",
    ]
