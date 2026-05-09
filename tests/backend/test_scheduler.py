from app.backend.scheduler.daily import build_trigger
from app.backend.services.daily_job.service import run_daily_job
from app.backend.cli.commands.schedule_screening import handle_schedule_screening


def test_scheduler_uses_jakarta_timezone():
    trigger = build_trigger()
    assert "Asia/Jakarta" in str(trigger.timezone)


def test_schedule_screening_registers_daily_job(monkeypatch):
    captured: dict[str, object] = {}

    class FakeScheduler:
        def add_job(self, func, trigger, id, replace_existing):
            captured["func"] = func
            captured["trigger"] = trigger
            captured["id"] = id
            captured["replace_existing"] = replace_existing

        def start(self):
            captured["started"] = True

    run_dates: list[str] = []

    def fake_run_daily_job(run_date: str):
        run_dates.append(run_date)

    monkeypatch.setattr("app.backend.cli.commands.schedule_screening.BackgroundScheduler", lambda timezone: FakeScheduler())
    monkeypatch.setattr("app.backend.cli.commands.schedule_screening._resolve_run_date", lambda: "2026-05-09")
    monkeypatch.setattr("app.backend.cli.commands.schedule_screening.run_daily_job", fake_run_daily_job)

    handle_schedule_screening("Asia/Jakarta")

    assert captured["id"] == "daily-screening"
    assert captured["replace_existing"] is True
    assert captured["started"] is True

    captured["func"]()
    assert run_dates == ["2026-05-09"]


def test_run_daily_job_delegates_to_cli_orchestration(monkeypatch):
    captured: dict[str, object] = {}

    def fake_handle_run_daily(date: str, preset: str, batch_size: int, qps: float, raise_on_error: bool = True) -> dict:
        captured["date"] = date
        captured["preset"] = preset
        captured["batch_size"] = batch_size
        captured["qps"] = qps
        captured["raise_on_error"] = raise_on_error
        return {"status": "success", "error": None}

    monkeypatch.setattr("app.backend.cli.main.handle_run_daily", fake_handle_run_daily)

    result = run_daily_job("2026-05-07", batch_size=25)

    assert result == {
        "status": "success",
        "skipped": False,
        "error": None,
    }
    assert captured == {
        "date": "2026-05-07",
        "preset": "balanced",
        "batch_size": 25,
        "qps": 2.0,
        "raise_on_error": False,
    }


def test_run_daily_job_maps_skipped_status(monkeypatch):
    def fake_handle_run_daily(date: str, preset: str, batch_size: int, qps: float, raise_on_error: bool = True) -> dict:
        return {"status": "skipped", "error": "already running or already executed"}

    monkeypatch.setattr("app.backend.cli.main.handle_run_daily", fake_handle_run_daily)

    result = run_daily_job("2026-05-07")

    assert result == {
        "status": "skipped",
        "skipped": True,
        "error": "already running or already executed",
    }


def test_run_daily_job_maps_failed_status(monkeypatch):
    def fake_handle_run_daily(date: str, preset: str, batch_size: int, qps: float, raise_on_error: bool = True) -> dict:
        return {"status": "failed", "error": "market source unavailable"}

    monkeypatch.setattr("app.backend.cli.main.handle_run_daily", fake_handle_run_daily)

    result = run_daily_job("2026-05-07")

    assert result == {
        "status": "failed",
        "skipped": False,
        "error": "market source unavailable",
    }
