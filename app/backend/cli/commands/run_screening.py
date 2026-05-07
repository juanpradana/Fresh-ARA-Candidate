from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_feature_rows_by_date, upsert_screening_result
from app.backend.services.scoring.service import score_candidate
from app.backend.services.screening.service import is_fresh_ara_candidate


def handle_run_screening(date: str, preset: str = "balanced", feature_version: str = "v1") -> None:
    init_db()
    rows = get_feature_rows_by_date(trade_date=date, feature_version=feature_version)

    for features in rows:
        passed = is_fresh_ara_candidate(features)
        score = score_candidate(features)
        pass_count = sum(
            [
                1 if 0.75 <= features["vol_ratio"] <= 1.25 else 0,
                1 if 0.50 <= features["range_pct"] <= 1.00 else 0,
                1 if features["price_action"] < 0.70 else 0,
                1 if int(features["is_ara_t0"]) == 0 else 0,
            ]
        )

        upsert_screening_result(
            screen_date=date,
            ticker=features["ticker"],
            preset_name=preset,
            score=score,
            pass_count=pass_count,
            category="ideal" if passed else "candidate",
        )
