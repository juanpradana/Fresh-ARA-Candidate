from apscheduler.triggers.cron import CronTrigger


def build_trigger(timezone: str = "Asia/Jakarta") -> CronTrigger:
    return CronTrigger(hour=18, minute=0, timezone=timezone)
