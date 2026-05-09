from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_backtest_summary, upsert_screening_result


def test_backtest_summary_includes_extended_metrics():
    init_db()
    upsert_screening_result(
        screen_date="2026-05-22",
        ticker="EXT1.JK",
        preset_name="balanced",
        score=0.95,
        pass_count=4,
        category="ideal",
    )
    upsert_screening_result(
        screen_date="2026-05-22",
        ticker="EXT2.JK",
        preset_name="balanced",
        score=0.80,
        pass_count=3,
        category="candidate",
    )

    summary = get_backtest_summary(start="2026-05-22", end="2026-05-22", preset="balanced", top_n=10)
    assert "hit_rate_1d" in summary
    assert "hit_rate_3d" in summary
    assert "avg_score_hit" in summary
    assert "avg_score_miss" in summary
    assert "distribution_by_pass_count" in summary
