from app.backend.scheduler.daily import build_trigger


def handle_schedule_screening(timezone: str = "Asia/Jakarta") -> None:
    trigger = build_trigger(timezone=timezone)
    print(str(trigger))
