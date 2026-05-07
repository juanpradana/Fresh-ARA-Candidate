from datetime import datetime, timedelta

from app.backend.cli.commands.update_market import handle_update_market


def handle_backfill_market(start: str, end: str, qps: float = 2.0, batch_size: int = 50) -> None:
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    while current <= end_date:
        handle_update_market(date=current.strftime("%Y-%m-%d"), batch_size=batch_size, qps=qps)
        current += timedelta(days=1)
