from datetime import datetime

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import (
    finish_job_run_failed,
    finish_job_run_success,
    try_start_job_run,
)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _run_daily(run_date: str, batch_size: int = 50) -> None:
    from app.backend.cli.main import _run_daily as cli_run_daily

    cli_run_daily(run_date, batch_size=batch_size)


def run_daily_job(run_date: str, batch_size: int = 50) -> dict:
    init_db()
    started_at = _now_iso()
    started = try_start_job_run(run_date=run_date, started_at=started_at)
    if not started:
        return {
            "status": "skipped",
            "skipped": True,
            "error": None,
        }

    try:
        _run_daily(run_date, batch_size)
        finish_job_run_success(run_date=run_date, finished_at=_now_iso())
        return {
            "status": "success",
            "skipped": False,
            "error": None,
        }
    except Exception as exc:
        finish_job_run_failed(
            run_date=run_date,
            finished_at=_now_iso(),
            error_message=str(exc),
        )
        return {
            "status": "failed",
            "skipped": False,
            "error": str(exc),
        }
