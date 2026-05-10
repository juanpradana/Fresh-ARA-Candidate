def score_price_action_tier(price_action: float) -> float:
    if price_action < 0.30:
        return 1.0
    if price_action < 0.50:
        return 0.8
    if price_action < 0.70:
        return 0.6
    return 0.0


def _clamp_zero_one(value: float) -> float:
    return max(0.0, min(1.0, value))


def _score_rsi14_zone(rsi14: float) -> float:
    distance_to_50 = abs(rsi14 - 50.0)
    return _clamp_zero_one(1.0 - distance_to_50 / 30.0)


def score_candidate(features: dict, feature_set: str = "legacy") -> float:
    base_scores = [
        max(0.0, 1.0 - abs(float(features["vol_ratio"]) - 1.0)),
        max(0.0, 1.0 - abs(float(features["range_pct"]) - 0.75)),
        score_price_action_tier(float(features["price_action"])),
    ]

    if feature_set != "rich_v1":
        return round(sum(base_scores) / len(base_scores), 4)

    rich_scores = [
        _clamp_zero_one(float(features.get("vol_ratio_3d", features["vol_ratio"])) / 2.0),
        _clamp_zero_one(float(features.get("vol_ratio_20", features["vol_ratio"])) / 2.0),
        _clamp_zero_one(float(features.get("rel_strength_5d_vs_jkse", 0.0)) / 5.0 + 0.5),
        _clamp_zero_one(1.0 - abs(float(features.get("price_vs_ma20_pct", 0.0))) / 20.0),
        _clamp_zero_one(1.0 - abs(float(features.get("price_vs_ma50_pct", 0.0))) / 25.0),
        _clamp_zero_one(float(features.get("float_ratio", 0.0))),
        _clamp_zero_one(float(features.get("value_traded", 0.0)) / 1_000_000_000.0),
        _clamp_zero_one(1.0 - float(features.get("bb_width", 0.0))),
        _clamp_zero_one(1.0 - float(features.get("range_volatility", 0.0)) / 10.0),
        _clamp_zero_one(float(features.get("consecutive_green_days", 0.0)) / 5.0),
        _score_rsi14_zone(float(features.get("rsi14", 0.0))),
        _clamp_zero_one(float(features.get("rsi14_slope", 0.0)) / 5.0 + 0.5),
        _clamp_zero_one(1.0 - abs(float(features.get("atr5_atr20_ratio", 1.0)) - 0.5) / 0.7),
        _clamp_zero_one(float(features.get("dist_to_52w_high_pct", -100.0)) / 50.0 + 1.0),
    ]
    scores = base_scores + rich_scores
    return round(sum(scores) / len(scores), 4)
