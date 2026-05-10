from app.backend.services.scoring.service import score_candidate, score_price_action_tier


def test_price_action_tiered_scoring_boundaries():
    assert score_price_action_tier(0.29) == 1.0
    assert score_price_action_tier(0.30) == 0.8
    assert score_price_action_tier(0.50) == 0.6
    assert score_price_action_tier(0.70) == 0.0


def test_rich_v1_scoring_uses_new_indicator_columns():
    base_features = {
        "vol_ratio": 1.0,
        "range_pct": 0.75,
        "price_action": 0.25,
        "vol_ratio_3d": 1.0,
        "vol_ratio_20": 1.0,
        "rel_strength_5d_vs_jkse": 0.5,
        "price_vs_ma20_pct": 1.0,
        "price_vs_ma50_pct": 2.0,
        "float_ratio": 0.6,
        "value_traded": 800_000_000.0,
        "bb_width": 0.2,
        "range_volatility": 1.2,
    }

    weak_new_indicators = {
        **base_features,
        "consecutive_green_days": 0,
        "rsi14": 20.0,
        "rsi14_slope": -2.0,
        "atr5_atr20_ratio": 1.5,
        "dist_to_52w_high_pct": -40.0,
    }

    strong_new_indicators = {
        **base_features,
        "consecutive_green_days": 4,
        "rsi14": 52.0,
        "rsi14_slope": 2.0,
        "atr5_atr20_ratio": 0.55,
        "dist_to_52w_high_pct": -3.0,
    }

    weak_score = score_candidate(weak_new_indicators, feature_set="rich_v1")
    strong_score = score_candidate(strong_new_indicators, feature_set="rich_v1")

    assert strong_score > weak_score
