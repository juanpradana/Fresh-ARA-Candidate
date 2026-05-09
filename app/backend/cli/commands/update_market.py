from typing import Callable

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_missing_tickers_for_date, upsert_price_daily
from app.backend.services.market_data import service as market_data_service
from app.backend.services.market_data.guardrails import CircuitBreaker, RequestCache, RateLimiter
from app.backend.services.universe.service import resolve_ticker_universe


def handle_update_market(
    date: str,
    batch_size: int = 50,
    qps: float = 2.0,
    on_event: Callable[[dict[str, object]], None] | None = None,
    universe_mode: str = "external_live",
) -> dict:
    init_db()
    universe = resolve_ticker_universe(mode=universe_mode)
    tickers = [str(ticker) for ticker in universe.get("tickers", [])]
    universe_source = str(universe.get("source", "default_idx_fallback"))
    universe_fallback = bool(universe.get("fallback_used", False))
    missing = get_missing_tickers_for_date(trade_date=date, tickers=tickers)
    limiter = RateLimiter(qps=qps) if qps > 0 else None
    breaker = CircuitBreaker(failure_threshold=5, reset_timeout=10.0)
    cache = RequestCache[list[dict]]()

    if on_event is not None:
        on_event(
            {
                "event": "update_market.universe_resolved",
                "date": date,
                "universe_mode": universe_mode,
                "universe_source": universe_source,
                "universe_count": len(tickers),
                "universe_fallback": universe_fallback,
            }
        )

    fetched = 0
    tickers_ok = 0
    tickers_empty = 0
    tickers_error = 0
    rows_upserted = 0
    batch_count = 0
    for index in range(0, len(missing), batch_size):
        batch_count += 1
        batch = missing[index:index + batch_size]
        for ticker in batch:
            try:
                rows = market_data_service.fetch_daily_market_data(
                    ticker=ticker,
                    date=date,
                    limiter=limiter,
                    breaker=breaker,
                    cache=cache,
                )
            except TypeError:
                rows = market_data_service.fetch_daily_market_data(ticker, date)
            except Exception as exc:
                tickers_error += 1
                if on_event is not None:
                    on_event(
                        {
                            "event": "update_market.ticker_outcome",
                            "date": date,
                            "ticker": ticker,
                            "outcome": "error",
                            "row_count": 0,
                            "error_type": type(exc).__name__,
                        }
                    )
                continue
            if rows:
                fetched += 1
                tickers_ok += 1
                outcome = "ok"
            else:
                tickers_empty += 1
                outcome = "empty"
            if on_event is not None:
                on_event(
                    {
                        "event": "update_market.ticker_outcome",
                        "date": date,
                        "ticker": ticker,
                        "outcome": outcome,
                        "row_count": len(rows),
                    }
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
                rows_upserted += 1

    expected = len(missing)
    result = {
        "date": date,
        "expected": expected,
        "fetched": fetched,
        "is_complete": fetched == expected,
        "tickers_ok": tickers_ok,
        "tickers_empty": tickers_empty,
        "tickers_error": tickers_error,
        "rows_upserted": rows_upserted,
        "batch_count": batch_count,
        "universe_mode": universe_mode,
        "universe_source": universe_source,
        "universe_count": len(tickers),
        "universe_fallback": universe_fallback,
    }
    if on_event is not None:
        on_event(
            {
                "event": "update_market.run_completed",
                "date": date,
                "expected": expected,
                "fetched": fetched,
                "is_complete": fetched == expected,
                "tickers_ok": tickers_ok,
                "tickers_empty": tickers_empty,
                "tickers_error": tickers_error,
                "rows_upserted": rows_upserted,
                "batch_count": batch_count,
                "universe_mode": universe_mode,
                "universe_source": universe_source,
                "universe_count": len(tickers),
                "universe_fallback": universe_fallback,
            }
        )
    return result
