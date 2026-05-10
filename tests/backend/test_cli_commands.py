import json

import pytest

from app.backend.cli.main import main as cli_main


def test_update_market_command_dispatches(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
        captured["date"] = date
        captured["batch_size"] = batch_size
        captured["qps"] = qps
        captured["universe_mode"] = universe_mode
        return {"is_complete": True, "expected": 0, "fetched": 0, "universe_source": universe_mode}

    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "update-market",
            "--date",
            "2026-05-07",
            "--batch-size",
            "25",
            "--qps",
            "2.5",
            "--universe-mode",
            "external_live",
        ],
    )

    cli_main()

    assert captured == {
        "date": "2026-05-07",
        "batch_size": 25,
        "qps": 2.5,
        "universe_mode": "external_live",
    }


def test_run_screening_command_dispatches(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(date: str, preset: str, feature_version: str = "v1") -> None:
        captured["date"] = date
        captured["preset"] = preset
        captured["feature_version"] = feature_version

    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "run-screening",
            "--date",
            "2026-05-07",
            "--preset",
            "aggressive",
            "--feature-version",
            "v2",
        ],
    )

    cli_main()

    assert captured == {
        "date": "2026-05-07",
        "preset": "aggressive",
        "feature_version": "v2",
    }


def test_compute_features_command_dispatches_date_mode(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(date: str, feature_version: str = "v1") -> None:
        captured["date"] = date
        captured["feature_version"] = feature_version

    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "compute-features", "--date", "2026-05-07", "--feature-version", "v2"],
    )

    cli_main()

    assert captured == {
        "date": "2026-05-07",
        "feature_version": "v2",
    }


def test_compute_features_command_dispatches_range_mode(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(start: str, end: str, feature_version: str = "v1") -> None:
        captured["start"] = start
        captured["end"] = end
        captured["feature_version"] = feature_version

    monkeypatch.setattr("app.backend.cli.main.handle_compute_features_range", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "compute-features",
            "--start",
            "2026-05-01",
            "--end",
            "2026-05-07",
            "--feature-version",
            "v2",
        ],
    )

    cli_main()

    assert captured == {
        "start": "2026-05-01",
        "end": "2026-05-07",
        "feature_version": "v2",
    }


def test_compute_features_rejects_mixed_date_and_range(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "compute-features",
            "--date",
            "2026-05-07",
            "--start",
            "2026-05-01",
            "--end",
            "2026-05-07",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        cli_main()

    assert exc.value.code == 2


def test_run_screening_command_dispatches_range_mode(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(start: str, end: str, preset: str = "balanced", feature_version: str = "v1") -> None:
        captured["start"] = start
        captured["end"] = end
        captured["preset"] = preset
        captured["feature_version"] = feature_version

    monkeypatch.setattr("app.backend.cli.main.handle_run_screening_range", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "run-screening",
            "--start",
            "2026-05-01",
            "--end",
            "2026-05-07",
            "--preset",
            "aggressive",
            "--feature-version",
            "v2",
        ],
    )

    cli_main()

    assert captured == {
        "start": "2026-05-01",
        "end": "2026-05-07",
        "preset": "aggressive",
        "feature_version": "v2",
    }


def test_run_screening_rejects_date_without_range_pair(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "run-screening", "--start", "2026-05-01", "--preset", "balanced"],
    )

    with pytest.raises(SystemExit) as exc:
        cli_main()

    assert exc.value.code == 2


def test_export_market_data_command_dispatches_date_mode(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(
        date: str | None,
        start: str | None,
        end: str | None,
        output: str,
        source: str | None,
        tickers: str | None,
        format: str = "csv",
    ) -> None:
        captured["date"] = date
        captured["start"] = start
        captured["end"] = end
        captured["output"] = output
        captured["source"] = source
        captured["tickers"] = tickers
        captured["format"] = format

    monkeypatch.setattr("app.backend.cli.main.handle_export_market_data", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "export-market-data",
            "--date",
            "2026-05-07",
            "--output",
            "data/market.csv",
        ],
    )

    cli_main()

    assert captured == {
        "date": "2026-05-07",
        "start": None,
        "end": None,
        "output": "data/market.csv",
        "source": None,
        "tickers": None,
        "format": "csv",
    }


def test_export_market_data_command_dispatches_range_mode(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handler(
        date: str | None,
        start: str | None,
        end: str | None,
        output: str,
        source: str | None,
        tickers: str | None,
        format: str = "csv",
    ) -> None:
        captured["date"] = date
        captured["start"] = start
        captured["end"] = end
        captured["output"] = output
        captured["source"] = source
        captured["tickers"] = tickers
        captured["format"] = format

    monkeypatch.setattr("app.backend.cli.main.handle_export_market_data", fake_handler, raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "export-market-data",
            "--start",
            "2026-05-01",
            "--end",
            "2026-05-07",
            "--output",
            "data/market.csv",
            "--source",
            "yfinance",
            "--tickers",
            "BBCA.JK,TLKM.JK",
            "--format",
            "parquet",
        ],
    )

    cli_main()

    assert captured == {
        "date": None,
        "start": "2026-05-01",
        "end": "2026-05-07",
        "output": "data/market.csv",
        "source": "yfinance",
        "tickers": "BBCA.JK,TLKM.JK",
        "format": "parquet",
    }


def test_export_market_data_rejects_missing_date_mode(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["cli", "export-market-data", "--output", "data/market.csv"],
    )

    with pytest.raises(SystemExit) as exc:
        cli_main()

    assert exc.value.code == 2


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

    def fake_update(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
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
    monkeypatch.setattr("app.backend.cli.main.capture_watchlist_alerts", lambda run_date, preset: 0, raising=False)
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

    def fake_update(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
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
    calls: list[dict[str, object]] = []

    def fake_init_db() -> None:
        calls.append({"event": "init"})

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append({"event": "start", "run_date": run_date})
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append(
            {
                "event": "success",
                "run_date": run_date,
                "rows": rows_affected,
                "meta": None if meta_json is None else json.loads(meta_json),
            }
        )

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(
            {
                "event": "failed",
                "run_date": run_date,
                "error": error_message,
                "rows": rows_affected,
                "meta": None if meta_json is None else json.loads(meta_json),
            }
        )

    def fake_update(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
        calls.append({"event": "update", "date": date, "batch_size": batch_size, "qps": qps})
        return {
            "is_complete": True,
            "fetched": 7,
            "expected": 10,
            "tickers_ok": 7,
            "tickers_empty": 2,
            "tickers_error": 1,
            "rows_upserted": 7,
            "batch_count": 1,
            "universe_source": "external_live",
            "universe_count": 10,
            "universe_fallback": False,
        }

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append({"event": "compute", "date": date, "feature_version": feature_version})

    def fake_screen(date: str, preset: str) -> None:
        calls.append({"event": "screen", "date": date, "preset": preset})

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("app.backend.cli.main.capture_watchlist_alerts", lambda run_date, preset: 0, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-09"])

    cli_main()

    assert [entry["event"] for entry in calls] == [
        "init",
        "start",
        "update",
        "compute",
        "screen",
        "success",
    ]
    success = calls[-1]
    assert success["run_date"] == "2026-05-09"
    assert success["rows"] == 7
    meta = success["meta"]
    assert meta == {
        "expected": 10,
        "fetched": 7,
        "preset": "balanced",
        "market_status": "complete",
        "tickers_ok": 7,
        "tickers_empty": 2,
        "tickers_error": 1,
        "rows_upserted": 7,
        "batch_count": 1,
        "universe_mode": "external_live",
        "universe_source": "external_live",
        "universe_count": 10,
        "universe_fallback": False,
    }


def test_run_daily_records_job_run_failed_when_incomplete(monkeypatch):
    calls: list[dict[str, object]] = []

    def fake_init_db() -> None:
        calls.append({"event": "init"})

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append({"event": "start", "run_date": run_date})
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append({"event": "success", "run_date": run_date, "rows": rows_affected, "meta": meta_json})

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(
            {
                "event": "failed",
                "run_date": run_date,
                "error": error_message,
                "rows": rows_affected,
                "meta": None if meta_json is None else json.loads(meta_json),
            }
        )

    def fake_skipped(
        run_date: str,
        finished_at: str,
        message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append({"event": "skipped", "run_date": run_date, "message": message, "rows": rows_affected, "meta": meta_json})

    def fake_update(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
        calls.append({"event": "update", "date": date, "batch_size": batch_size, "qps": qps})
        return {
            "is_complete": False,
            "expected": 10,
            "fetched": 3,
            "tickers_ok": 3,
            "tickers_empty": 5,
            "tickers_error": 2,
            "rows_upserted": 6,
            "batch_count": 1,
            "universe_source": "external_live",
            "universe_count": 10,
            "universe_fallback": False,
        }

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append({"event": "compute", "date": date, "feature_version": feature_version})

    def fake_screen(date: str, preset: str) -> None:
        calls.append({"event": "screen", "date": date, "preset": preset})

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    alarm_codes: list[str] = []

    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_skipped", fake_skipped, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.main._emit_system_alarm",
        lambda run_date, code: alarm_codes.append(code) or True,
        raising=False,
    )
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-09"])

    cli_main()

    assert [entry["event"] for entry in calls] == ["init", "start", "update", "failed"]
    assert alarm_codes == ["system.market_data_incomplete"]
    failed = calls[-1]
    assert failed["error"] == "market data incomplete"
    assert failed["rows"] == 3
    assert failed["meta"] == {
        "expected": 10,
        "fetched": 3,
        "preset": "balanced",
        "market_status": "partial",
        "tickers_ok": 3,
        "tickers_empty": 5,
        "tickers_error": 2,
        "rows_upserted": 6,
        "batch_count": 1,
        "universe_mode": "external_live",
        "universe_source": "external_live",
        "universe_count": 10,
        "universe_fallback": False,
    }


def test_run_daily_records_job_run_skipped_when_no_market_data(monkeypatch):
    calls: list[dict[str, object]] = []

    def fake_init_db() -> None:
        calls.append({"event": "init"})

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append({"event": "start", "run_date": run_date})
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append({"event": "success", "run_date": run_date, "rows": rows_affected, "meta": meta_json})

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append({"event": "failed", "run_date": run_date, "error": error_message, "rows": rows_affected, "meta": meta_json})

    def fake_skipped(
        run_date: str,
        finished_at: str,
        message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(
            {
                "event": "skipped",
                "run_date": run_date,
                "message": message,
                "rows": rows_affected,
                "meta": None if meta_json is None else json.loads(meta_json),
            }
        )

    def fake_update(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
        calls.append({"event": "update", "date": date, "batch_size": batch_size, "qps": qps})
        return {
            "is_complete": False,
            "expected": 5,
            "fetched": 0,
            "tickers_ok": 0,
            "tickers_empty": 5,
            "tickers_error": 0,
            "rows_upserted": 0,
            "batch_count": 1,
            "universe_source": "external_live",
            "universe_count": 5,
            "universe_fallback": False,
        }

    def fake_compute(date: str, feature_version: str) -> None:
        calls.append({"event": "compute", "date": date, "feature_version": feature_version})

    def fake_screen(date: str, preset: str) -> None:
        calls.append({"event": "screen", "date": date, "preset": preset})

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    alarm_codes: list[str] = []

    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_skipped", fake_skipped, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.main._emit_system_alarm",
        lambda run_date, code: alarm_codes.append(code) or True,
        raising=False,
    )
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", fake_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", fake_screen, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-11"])

    cli_main()

    assert [entry["event"] for entry in calls] == ["init", "start", "update", "skipped"]
    assert alarm_codes == ["system.no_market_data"]
    skipped = calls[-1]
    assert skipped["message"] == "no market data"
    assert skipped["rows"] == 0
    assert skipped["meta"] == {
        "expected": 5,
        "fetched": 0,
        "preset": "balanced",
        "market_status": "empty",
        "tickers_ok": 0,
        "tickers_empty": 5,
        "tickers_error": 0,
        "rows_upserted": 0,
        "batch_count": 1,
        "universe_mode": "external_live",
        "universe_source": "external_live",
        "universe_count": 5,
        "universe_fallback": False,
    }


def test_daily_smoke_prints_ok_for_success(monkeypatch, capsys):
    def fake_smoke(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
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
    def fake_smoke(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
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
    def fake_smoke(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
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


def test_run_daily_records_job_run_failed_on_exception_with_metrics(monkeypatch):
    calls: list[dict[str, object]] = []

    def fake_init_db() -> None:
        calls.append({"event": "init"})

    def fake_start(run_date: str, started_at: str) -> bool:
        calls.append({"event": "start", "run_date": run_date})
        return True

    def fake_success(run_date: str, finished_at: str, rows_affected: int = 0, meta_json: str | None = None) -> None:
        calls.append({"event": "success", "run_date": run_date, "rows": rows_affected, "meta": meta_json})

    def fake_failed(
        run_date: str,
        finished_at: str,
        error_message: str,
        rows_affected: int = 0,
        meta_json: str | None = None,
    ) -> None:
        calls.append(
            {
                "event": "failed",
                "run_date": run_date,
                "error": error_message,
                "rows": rows_affected,
                "meta": None if meta_json is None else json.loads(meta_json),
            }
        )

    def fake_update(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
        calls.append({"event": "update", "date": date, "batch_size": batch_size, "qps": qps})
        return {
            "is_complete": True,
            "expected": 9,
            "fetched": 4,
            "universe_source": "external_live",
            "universe_count": 9,
            "universe_fallback": False,
        }

    def boom_compute(date: str, feature_version: str) -> None:
        calls.append({"event": "compute", "date": date, "feature_version": feature_version})
        raise RuntimeError("compute exploded")

    monkeypatch.setattr("app.backend.cli.main.init_db", fake_init_db, raising=False)
    monkeypatch.setattr("app.backend.cli.main.try_start_job_run", fake_start, raising=False)
    alarm_codes: list[str] = []

    monkeypatch.setattr("app.backend.cli.main.finish_job_run_success", fake_success, raising=False)
    monkeypatch.setattr("app.backend.cli.main.finish_job_run_failed", fake_failed, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.main._emit_system_alarm",
        lambda run_date, code: alarm_codes.append(code) or True,
        raising=False,
    )
    monkeypatch.setattr("app.backend.cli.main.handle_update_market", fake_update, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_compute_features", boom_compute, raising=False)
    monkeypatch.setattr("app.backend.cli.main.handle_run_screening", lambda date, preset: None, raising=False)
    monkeypatch.setattr("app.backend.cli.main.capture_watchlist_alerts", lambda run_date, preset: 0, raising=False)
    monkeypatch.setattr("sys.argv", ["cli", "run-daily", "--date", "2026-05-13"])

    with pytest.raises(RuntimeError) as exc:
        cli_main()

    assert "compute exploded" in str(exc.value)
    assert alarm_codes == ["system.exception.RuntimeError"]
    assert [entry["event"] for entry in calls] == ["init", "start", "update", "compute", "failed"]
    failed = calls[-1]
    assert failed["run_date"] == "2026-05-13"
    assert failed["error"] == "compute exploded"
    assert failed["rows"] == 4
    assert failed["meta"] == {
        "expected": 9,
        "fetched": 4,
        "preset": "balanced",
        "market_status": "complete",
        "tickers_ok": 0,
        "tickers_empty": 0,
        "tickers_error": 0,
        "rows_upserted": 0,
        "batch_count": 0,
        "universe_mode": "external_live",
        "universe_source": "external_live",
        "universe_count": 9,
        "universe_fallback": False,
    }
