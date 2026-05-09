from app.backend.services.feature_engineering.service import compute_features


def test_compute_features_uses_vol_ratio_5d():
    row = {
        "volume": 1000.0,
        "prev_volume": 900.0,
        "avg_volume_5d": 800.0,
        "high": 105.0,
        "low": 100.0,
        "close": 102.0,
        "open": 101.0,
    }

    out = compute_features(row)
    assert round(out["vol_ratio"], 4) == 1.25
