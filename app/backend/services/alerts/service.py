from datetime import datetime

from app.backend.repositories.sqlite.repo import (
    create_alert_event,
    get_screening_tickers,
    list_watchlists,
    list_watchlist_tickers,
)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def capture_watchlist_alerts(run_date: str, preset: str = "balanced") -> int:
    screening_tickers = set(get_screening_tickers(screen_date=run_date, preset=preset))
    if not screening_tickers:
        return 0

    inserted = 0
    watchlists = list_watchlists()
    for watchlist in watchlists:
        watchlist_name = str(watchlist["watchlist_name"])
        rows = list_watchlist_tickers(watchlist_name=watchlist_name)
        for row in rows:
            ticker = str(row["ticker"])
            if ticker not in screening_tickers:
                continue
            created = create_alert_event(
                run_date=run_date,
                watchlist_name=watchlist_name,
                ticker=ticker,
                preset=preset,
                created_at=_now_iso(),
            )
            if created:
                inserted += 1

    return inserted
