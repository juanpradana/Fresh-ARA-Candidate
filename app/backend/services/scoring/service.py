def score_price_action_tier(price_action: float) -> float:
    if price_action < 0.30:
        return 1.0
    if price_action < 0.50:
        return 0.8
    if price_action < 0.70:
        return 0.6
    return 0.0


def score_candidate(features: dict) -> float:
    score = 0.0
    score += max(0.0, 1.0 - abs(features["vol_ratio"] - 1.0))
    score += max(0.0, 1.0 - abs(features["range_pct"] - 0.75))
    score += score_price_action_tier(float(features["price_action"]))
    return round(score / 3.0, 4)
