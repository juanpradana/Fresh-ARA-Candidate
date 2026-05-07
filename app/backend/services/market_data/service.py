import yfinance as yf

from app.backend.services.market_data.guardrails import (
    CircuitBreaker,
    RequestCache,
    RateLimiter,
    retry_with_backoff,
)


def fetch_daily_market_data(
    ticker: str,
    date: str,
    limiter: RateLimiter | None = None,
    breaker: CircuitBreaker | None = None,
    cache: RequestCache[list[dict]] | None = None,
    max_attempts: int = 3,
    base_delay: float = 0.2,
    max_delay: float = 2.0,
    jitter_ratio: float = 0.1,
) -> list[dict]:
    key = (ticker, date)
    if cache is not None and cache.has(key):
        return cache.get(key)

    if breaker is not None and not breaker.allow():
        return []

    if limiter is not None:
        limiter.wait()

    def operation() -> list[dict]:
        history = yf.Ticker(ticker).history(start=date, end=date)
        previous = yf.Ticker(ticker).history(period="5d")

        if history.empty:
            return []

        row = history.iloc[-1]
        prev_volume = float(previous.iloc[-2]["Volume"]) if len(previous) >= 2 else float(row["Volume"])
        prev_close = float(previous.iloc[-2]["Close"]) if len(previous) >= 2 else float(row["Close"])

        return [
            {
                "ticker": ticker,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
                "prev_volume": prev_volume,
                "prev_close": prev_close,
            }
        ]

    try:
        rows = retry_with_backoff(
            operation=operation,
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            jitter_ratio=jitter_ratio,
        )
        if breaker is not None:
            breaker.record_success()
        if cache is not None:
            cache.set(key, rows)
        return rows
    except Exception:
        if breaker is not None:
            breaker.record_failure()
        raise
