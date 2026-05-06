from apscheduler.triggers.cron import CronTrigger


def build_trigger() -> CronTrigger:
    return CronTrigger(hour=18, minute=0, timezone="Asia/Jakarta")
