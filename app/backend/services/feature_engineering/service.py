def _pct_distance(value: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (value / baseline - 1.0) * 100.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _consecutive_green_days(row: dict) -> int:
    if "consecutive_green_days" in row:
        return int(row.get("consecutive_green_days", 0) or 0)

    streak = 0
    current_close = float(row.get("close", 0.0) or 0.0)
    for index in range(1, 8):
        prev_key = f"close_prev_{index}"
        prev_close = row.get(prev_key)
        if prev_close is None:
            break
        prev_value = float(prev_close or 0.0)
        if current_close > prev_value:
            streak += 1
            current_close = prev_value
            continue
        break
    return streak


def compute_features(row: dict) -> dict:
    volume = float(row.get("volume", 0.0) or 0.0)
    close = float(row.get("close", 0.0) or 0.0)
    open_price = float(row.get("open", 0.0) or 0.0)
    high = float(row.get("high", 0.0) or 0.0)
    low = float(row.get("low", 0.0) or 0.0)

    prev_close = float(row.get("prev_close", close) or close)
    avg_volume_3d = float(row.get("avg_volume_3d", 0.0) or 0.0)
    avg_volume_5d = float(row.get("avg_volume_5d", 0.0) or 0.0)
    avg_volume_20d = float(row.get("avg_volume_20d", 0.0) or 0.0)

    ma20 = float(row.get("ma20", close) or close)
    ma50 = float(row.get("ma50", close) or close)
    ticker_return_5d_pct = float(row.get("ticker_return_5d_pct", 0.0) or 0.0)
    jkse_return_5d_pct = float(row.get("jkse_return_5d_pct", 0.0) or 0.0)

    float_shares = float(row.get("float_shares", 0.0) or 0.0)
    shares_outstanding = float(row.get("shares_outstanding", 0.0) or 0.0)

    rsi14 = float(row.get("rsi14", 0.0) or 0.0)
    rsi14_prev = float(row.get("rsi14_prev", rsi14) or rsi14)
    atr5 = float(row.get("atr5", 0.0) or 0.0)
    atr20 = float(row.get("atr20", 0.0) or 0.0)
    high_52w = float(row.get("high_52w", close) or close)

    range_pct = ((high - low) / close * 100.0) if close else 0.0
    price_action = abs(close - open_price) / open_price if open_price else 0.0

    vol_ratio_3d = _safe_ratio(volume, avg_volume_3d)
    vol_ratio_5d = _safe_ratio(volume, avg_volume_5d)
    vol_ratio_20d = _safe_ratio(volume, avg_volume_20d)

    return {
        "vol_ratio": vol_ratio_5d,
        "range_pct": range_pct,
        "price_action": price_action,
        "is_ara_t0": int(row.get("is_ara_t0", 0)),
        "days_since_last_ara": int(row.get("days_since_last_ara", 999)),
        "daily_return_pct": _pct_distance(close, prev_close),
        "vol_ratio_3d": vol_ratio_3d,
        "vol_ratio_5d": vol_ratio_5d,
        "vol_ratio_20": vol_ratio_20d,
        "cpr": (high + low + close) / 3.0 if close else 0.0,
        "range_volatility": float(row.get("range_volatility", 0.0) or 0.0),
        "bb_width": float(row.get("bb_width", 0.0) or 0.0),
        "is_bb_squeeze_20": int(row.get("is_bb_squeeze_20", 0)),
        "price_vs_ma20_pct": _pct_distance(close, ma20),
        "price_vs_ma50_pct": _pct_distance(close, ma50),
        "value_traded": close * volume,
        "rel_strength_5d_vs_jkse": ticker_return_5d_pct - jkse_return_5d_pct,
        "float_shares": float_shares,
        "shares_outstanding": shares_outstanding,
        "float_ratio": _safe_ratio(float_shares, shares_outstanding),
        "consecutive_green_days": _consecutive_green_days(row),
        "rsi14": rsi14,
        "rsi14_slope": rsi14 - rsi14_prev,
        "atr5_atr20_ratio": _safe_ratio(atr5, atr20),
        "dist_to_52w_high_pct": _pct_distance(close, high_52w),
        "is_ara_next_day": int(row.get("is_ara_next_day", 0)),
    }
