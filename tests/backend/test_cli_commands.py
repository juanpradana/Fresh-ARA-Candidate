import pytest

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

    def fake_update(date: str, batch_size: int, qps: float) -> dict:
        calls.append(f"update:{date}:{batch_size}:{qps}")
        return {"is_complete": True}

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append(f"compute:{date}:{feature_version}")

    def fake_screen(date: str, preset: str) -> None:
        calls.append(f"screen:{date}:{preset}")

    def fail_legacy(_: str, batch_size: int = 50) -> None:
        raise AssertionError(f"legacy run_daily_job should not be called ({batch_size})")

    monkeypatch.setattr("app.backend.cli.main.init_db", lambda: None, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", lambda run_date, started_at: True, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.main.finish_job_run_success",
        lambda run_date, finished_at, rows_affected=0, meta_json=None: None,
        raising=False,
    )
    monkeypatch.setattr(
        "app.backend.cli.main.finish_job_run_failed",
        lambda run_date, finished_at, error_message, rows_affected=0, meta_json=None: None,
        raising=False,
    )
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


def test_run_daily_blocks_when_market_data_incomplete(monkeypatch):
    calls: list[str] = []

    def fake_update(date: str, batch_size: int, qps: float) -> dict:
        calls.append(f"update:{date}:{batch_size}:{qps}")
        return {"is_complete": False}

    def fake_compute(_: str, __: str) -> None:
        calls.append("compute")

    def fake_screen(_: str, __: str) -> None:
        calls.append("screen")

    monkeypatch.setattr("app.backend.cli.main.init_db", lambda: None, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", lambda run_date, started_at: True, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.main.finish_job_run_success",
        lambda run_date, finished_at, rows_affected=0, meta_json=None: None,
        raising=False,
    )
    monkeypatch.setattr(
        "app.backend.cli.main.finish_job_run_failed",
        lambda run_date, finished_at, error_message, rows_affected=0, meta_json=None: None,
        raising=False,
    )
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "run-daily", "--date", "2026-05-07"],
    )

    cli_main()

    assert calls == ["update:2026-05-07:50:2.0"]


def test_run_daily_records_job_run_success(monkeypatch):
    calls: list[str] = []

    def fake_init_db() -> None:
        calls.append("init")

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append(f"start:{run_date}")
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append(f"success:{run_date}:{rows_affected}:{meta_json}")

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(f"failed:{run_date}:{error_message}:{rows_affected}:{meta_json}")

    def fake_update(date: str, batch_size: int, qps: float) -> dict:
        calls.append(f"update:{date}:{batch_size}:{qps}")
        return {"is_complete": True, "fetched": 7, "expected": 10}

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append(f"compute:{date}:{feature_version}")

    def fake_screen(date: str, preset: str) -> None:
        calls.append(f"screen:{date}:{preset}")

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-09"])

    cli_main()

    assert calls == [
        "init",
        "start:2026-05-09",
        "update:2026-05-09:50:2.0",
        "compute:2026-05-09:v1",
        "screen:2026-05-09:balanced",
        'success:2026-05-09:7:{"expected":10,"fetched":7,"preset":"balanced"}',
    ]


def test_run_daily_records_job_run_failed_when_incomplete(monkeypatch):
    calls: list[str] = []

    def fake_init_db() -> None:
        calls.append("init")

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append(f"start:{run_date}")
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append(f"success:{run_date}:{rows_affected}:{meta_json}")

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(f"failed:{run_date}:{error_message}:{rows_affected}:{meta_json}")

    def fake_skipped(
        run_date: str,
        finished_at: str,
        message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(f"skipped:{run_date}:{message}:{rows_affected}:{meta_json}")

    def fake_update(date: str, batch_size: int, qps: float) -> dict:
        calls.append(f"update:{date}:{batch_size}:{qps}")
        return {"is_complete": False, "expected": 10, "fetched": 3}

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append(f"compute:{date}:{feature_version}")

    def fake_screen(date: str, preset: str) -> None:
        calls.append(f"screen:{date}:{preset}")

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_skipped", fake_skipped, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-09"])

    cli_main()

    assert calls == [
        "init",
        "start:2026-05-09",
        "update:2026-05-09:50:2.0",
        'failed:2026-05-09:market data incomplete:3:{"expected":10,"fetched":3,"preset":"balanced"}',
    ]


def test_run_daily_records_job_run_skipped_when_no_market_data(monkeypatch):
    calls: list[str] = []

    def fake_init_db() -> None:
        calls.append("init")

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append(f"start:{run_date}")
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append(f"success:{run_date}:{rows_affected}:{meta_json}")

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(f"failed:{run_date}:{error_message}:{rows_affected}:{meta_json}")

    def fake_skipped(
        run_date: str,
        finished_at: str,
        message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(f"skipped:{run_date}:{message}:{rows_affected}:{meta_json}")

    def fake_update(date: str, batch_size: int, qps: float) -> dict:
        calls.append(f"update:{date}:{batch_size}:{qps}")
        return {"is_complete": False, "expected": 5, "fetched": 0}

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append(f"compute:{date}:{feature_version}")

    def fake_screen(date: str, preset: str) -> None:
        calls.append(f"screen:{date}:{preset}")

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_skipped", fake_skipped, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-11"])

    cli_main()

    assert calls == [
        "init",
        "start:2026-05-11",
        "update:2026-05-11:50:2.0",
        'skipped:2026-05-11:no market data:0:{"expected":5,"fetched":0,"preset":"balanced"}',
    ]


def test_daily_smoke_prints_ok_for_success(monkeypatch, capsys):
    def fake_smoke(date: str, batch_size: int, qps: float) -> dict:
        assert date == "2026-05-09"
        assert batch_size == 25
        assert qps == 2.5
        return {"status": "success", "skipped": False, "error": None}

    monkeypatch.setattr("app.backend.cli.main.handle_daily_smoke", fake_smoke, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "daily-smoke", "--date", "2026-05-09", "--batch-size", "25", "--qps", "2.5"],
    )

    cli_main()

    output = capsys.readouterr().out
    assert "[SMOKE][OK] run_date=2026-05-09" in output


def test_daily_smoke_prints_skipped_for_non_trading_day(monkeypatch, capsys):
    def fake_smoke(date: str, batch_size: int, qps: float) -> dict:
        assert date == "2026-05-11"
        return {"status": "skipped", "skipped": True, "error": "no market data"}

    monkeypatch.setattr("app.backend.cli.main.handle_daily_smoke", fake_smoke, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "daily-smoke", "--date", "2026-05-11"],
    )

    cli_main()

    output = capsys.readouterr().out
    assert "[SMOKE][SKIPPED] run_date=2026-05-11 reason=no market data" in output


def test_daily_smoke_prints_alert_and_exits_for_failure(monkeypatch, capsys):
    def fake_smoke(date: str, batch_size: int, qps: float) -> dict:
        assert date == "2026-05-12"
        return {"status": "failed", "skipped": False, "error": "market source unavailable"}

    monkeypatch.setattr("app.backend.cli.main.handle_daily_smoke", fake_smoke, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "daily-smoke", "--date", "2026-05-12"],
    )

    with pytest.raises(SystemExit) as exc:
        cli_main()

    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "[SMOKE][ALERT] run_date=2026-05-12 error=market source unavailable" in output
