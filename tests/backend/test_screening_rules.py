from app.backend.services.screening.service import is_fresh_ara_candidate


def test_balanced_rule_passes_quiet_setup():
    row = {
        "vol_ratio": 1.0,
        "range_pct": 0.8,
        "price_action": 0.6,
        "is_ara_t0": 0,
    }
    assert is_fresh_ara_candidate(row)
