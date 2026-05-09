from app.backend.services.scoring.service import score_price_action_tier


def test_price_action_tiered_scoring_boundaries():
    assert score_price_action_tier(0.29) == 1.0
    assert score_price_action_tier(0.30) == 0.8
    assert score_price_action_tier(0.50) == 0.6
    assert score_price_action_tier(0.70) == 0.0
