from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_missing_tickers_for_date, upsert_price_daily
from app.backend.services.market_data.guardrails import CircuitBreaker, RequestCache, RateLimiter
from app.backend.services.market_data.service import fetch_daily_market_data
from app.backend.services.universe.service import get_default_idx_universe


def handle_update_market(date: str, batch_size: int = 50, qps: float = 2.0) -> None:
    init_db()
    tickers = get_default_idx_universe()
    missing = get_missing_tickers_for_date(trade_date=date, tickers=tickers)
    limiter = RateLimiter(qps=qps) if qps > 0 else None
    breaker = CircuitBreaker(failure_threshold=5, reset_timeout=10.0)
    cache = RequestCache[list[dict]]()

    for index in range(0, len(missing), batch_size):
        batch = missing[index:index + batch_size]
        for ticker in batch:
            rows = fetch_daily_market_data(
                ticker=ticker,
                date=date,
                limiter=limiter,
                breaker=breaker,
                cache=cache,
            )
            for row in rows:
                upsert_price_daily(
                    trade_date=date,
                    ticker=row["ticker"],
                    open_price=row["open"],
                    high_price=row["high"],
                    low_price=row["low"],
                    close_price=row["close"],
                    volume=row["volume"],
                    source="yfinance",
                )
