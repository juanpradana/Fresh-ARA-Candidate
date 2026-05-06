def score_candidate(features: dict) -> float:
    score = 0.0
    score += max(0.0, 1.0 - abs(features["vol_ratio"] - 1.0))
    score += max(0.0, 1.0 - abs(features["range_pct"] - 0.75))
    score += max(0.0, 1.0 - features["price_action"])
    return round(score / 3.0, 4)
