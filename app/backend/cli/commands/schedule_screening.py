from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.backend.scheduler.daily import build_trigger
from app.backend.services.daily_job.service import run_daily_job


_scheduler: BackgroundScheduler | None = None


def _resolve_run_date() -> str:
    return datetime.now().date().isoformat()


def _run_scheduled_daily_job() -> None:
    run_daily_job(run_date=_resolve_run_date())


def handle_schedule_screening(timezone: str = "Asia/Jakarta") -> None:
    global _scheduler
    trigger = build_trigger(timezone=timezone)
    scheduler = BackgroundScheduler(timezone=timezone)
    scheduler.add_job(
        _run_scheduled_daily_job,
        trigger=trigger,
        id="daily-screening",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    print(str(trigger))
