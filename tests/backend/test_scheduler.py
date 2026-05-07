from app.backend.scheduler.daily import build_trigger
from app.backend.services.daily_job.service import run_daily_job


def test_scheduler_uses_jakarta_timezone():
    trigger = build_trigger()
    assert "Asia/Jakarta" in str(trigger.timezone)


def test_run_daily_job_writes_success_log(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "scheduler.sqlite"))

    def fake_run_daily(_: str, __: int = 50) -> None:
        return None

    monkeypatch.setattr("app.backend.services.daily_job.service._run_daily", fake_run_daily)

    result = run_daily_job("2026-05-07")

    assert result["status"] == "success"
    assert result["skipped"] is False


def test_run_daily_job_skips_when_lock_exists(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "scheduler.sqlite"))

    first_call = {"entered": False}

    def fake_run_daily(_: str, __: int = 50) -> None:
        if not first_call["entered"]:
            first_call["entered"] = True
            raise RuntimeError("simulated failure")

    monkeypatch.setattr("app.backend.services.daily_job.service._run_daily", fake_run_daily)

    first = run_daily_job("2026-05-07")
    second = run_daily_job("2026-05-07")

    assert first["status"] == "failed"
    assert second["status"] == "skipped"
    assert second["skipped"] is True


def test_run_daily_job_persists_error_status(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "scheduler.sqlite"))

    def fake_run_daily(_: str, __: int = 50) -> None:
        raise ValueError("market source unavailable")

    monkeypatch.setattr("app.backend.services.daily_job.service._run_daily", fake_run_daily)

    result = run_daily_job("2026-05-07")

    assert result["status"] == "failed"
    assert "market source unavailable" in result["error"]
