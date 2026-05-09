import yfinance as yf


def get_default_idx_universe() -> list[str]:
    return [
        "BBCA.JK",
        "BBRI.JK",
        "BMRI.JK",
        "TLKM.JK",
        "ASII.JK",
    ]


def _normalize_ticker(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    value = raw.strip().upper()
    if not value:
        return None
    if "." in value and not value.endswith(".JK"):
        return None
    if not value.endswith(".JK"):
        value = f"{value}.JK"
    return value


def _sanitize_tickers(raw_tickers: list[object]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in raw_tickers:
        ticker = _normalize_ticker(raw)
        if ticker is None or ticker in seen:
            continue
        seen.add(ticker)
        cleaned.append(ticker)
    return cleaned


def get_external_live_idx_universe(max_results: int = 250) -> list[str]:
    try:
        frame = yf.Lookup("Indonesia", raise_errors=False).get_stock(count=max_results)
    except Exception:
        return []

    if getattr(frame, "empty", True):
        return []

    symbols: list[str] = []
    for symbol, row in frame.iterrows():
        exchange = str(row.get("exchange", "")).upper()
        quote_type = str(row.get("quoteType", "")).lower()
        if exchange != "JKT":
            continue
        if quote_type != "equity":
            continue
        symbols.append(str(symbol))

    return _sanitize_tickers(symbols)


def resolve_ticker_universe(mode: str = "external_live") -> dict[str, object]:
    normalized = mode.strip().lower()
    if normalized == "default_idx":
        tickers = get_default_idx_universe()
        return {
            "tickers": tickers,
            "source": "default_idx",
            "fallback_used": False,
        }

    if normalized == "external_live":
        tickers = get_external_live_idx_universe()
        if tickers:
            return {
                "tickers": tickers,
                "source": "external_live",
                "fallback_used": False,
            }
        fallback = get_default_idx_universe()
        return {
            "tickers": fallback,
            "source": "default_idx_fallback",
            "fallback_used": True,
        }

    fallback = get_default_idx_universe()
    return {
        "tickers": fallback,
        "source": "default_idx_fallback",
        "fallback_used": True,
    }
