from app.backend.services.screening.service import is_fresh_ara_candidate


def test_conservative_rejects_while_aggressive_accepts_same_row():
    row = {
        "vol_ratio": 0.65,
        "range_pct": 0.45,
        "price_action": 0.65,
        "is_ara_t0": 0,
    }

    conservative = {
        "vol_ratio_min": 0.85,
        "vol_ratio_max": 1.15,
        "range_pct_min": 0.50,
        "range_pct_max": 0.85,
        "price_action_max": 0.50,
    }

    aggressive = {
        "vol_ratio_min": 0.60,
        "vol_ratio_max": 1.40,
        "range_pct_min": 0.40,
        "range_pct_max": 1.20,
        "price_action_max": 0.90,
    }

    assert is_fresh_ara_candidate(row, conservative) is False
    assert is_fresh_ara_candidate(row, aggressive) is True
