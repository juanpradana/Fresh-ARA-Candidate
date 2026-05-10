from app.backend.services.feature_engineering.service import compute_features


def test_compute_features_uses_vol_ratio_5d():
    row = {
        "volume": 1000.0,
        "prev_volume": 900.0,
        "avg_volume_3d": 700.0,
        "avg_volume_5d": 800.0,
        "avg_volume_20d": 900.0,
        "high": 105.0,
        "low": 100.0,
        "close": 102.0,
        "open": 101.0,
        "prev_close": 100.0,
        "ma20": 98.0,
        "ma50": 95.0,
        "jkse_return_5d_pct": 1.0,
        "ticker_return_5d_pct": 2.0,
        "days_since_last_ara": 6,
        "is_ara_t0": 0,
        "float_shares": 40000000000.0,
        "shares_outstanding": 50000000000.0,
        "bb_width": 0.12,
        "is_bb_squeeze_20": 1,
        "range_volatility": 1.5,
        "consecutive_green_days": 4,
        "rsi14": 55.0,
        "rsi14_prev": 52.0,
        "atr5": 2.0,
        "atr20": 4.0,
        "high_52w": 120.0,
        "is_ara_next_day": 0,
    }

    out = compute_features(row)
    assert round(out["vol_ratio"], 4) == 1.25
    assert round(out["daily_return_pct"], 4) == 2.0
    assert round(out["vol_ratio_3d"], 4) == round(1000.0 / 700.0, 4)
    assert round(out["vol_ratio_5d"], 4) == 1.25
    assert round(out["vol_ratio_20"], 4) == round(1000.0 / 900.0, 4)
    assert round(out["cpr"], 4) == round((105.0 + 100.0 + 102.0) / 3.0, 4)
    assert round(out["price_vs_ma20_pct"], 4) == round((102.0 / 98.0 - 1.0) * 100.0, 4)
    assert round(out["price_vs_ma50_pct"], 4) == round((102.0 / 95.0 - 1.0) * 100.0, 4)
    assert out["value_traded"] == 102000.0
    assert out["rel_strength_5d_vs_jkse"] == 1.0
    assert out["float_ratio"] == 0.8
    assert out["is_bb_squeeze_20"] == 1
    assert out["consecutive_green_days"] == 4
    assert out["rsi14"] == 55.0
    assert out["rsi14_slope"] == 3.0
    assert out["atr5_atr20_ratio"] == 0.5
    assert round(out["dist_to_52w_high_pct"], 4) == round((102.0 / 120.0 - 1.0) * 100.0, 4)
    assert out["is_ara_next_day"] == 0
