def compute_features(row: dict) -> dict:
    avg_volume_5d = row.get("avg_volume_5d")
    vol_ratio = row["volume"] / avg_volume_5d if avg_volume_5d else 0.0
    range_pct = ((row["high"] - row["low"]) / row["close"] * 100.0) if row["close"] else 0.0
    price_action = abs(row["close"] - row["open"]) / row["open"] if row["open"] else 0.0

    return {
        "vol_ratio": vol_ratio,
        "range_pct": range_pct,
        "price_action": price_action,
        "is_ara_t0": 0,
        "days_since_last_ara": int(row.get("days_since_last_ara", 999)),
    }
