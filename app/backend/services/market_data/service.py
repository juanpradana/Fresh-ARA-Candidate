import yfinance as yf


def fetch_daily_market_data(ticker: str, date: str) -> list[dict]:
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
