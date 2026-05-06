from app.backend.scheduler.daily import build_trigger


def test_scheduler_uses_jakarta_timezone():
    trigger = build_trigger()
    assert "Asia/Jakarta" in str(trigger.timezone)
