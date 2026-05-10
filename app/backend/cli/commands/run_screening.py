from datetime import datetime, timedelta

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_default_presets, get_feature_rows_by_date, upsert_screening_result
from app.backend.services.scoring.service import score_candidate
from app.backend.services.screening.service import is_fresh_ara_candidate


def _resolve_preset(preset_name: str) -> dict[str, float]:
    presets = get_default_presets()
    selected = next((item for item in presets if item["preset_name"] == preset_name), None)
    if selected is not None:
        return selected
    fallback = next((item for item in presets if item["preset_name"] == "balanced"), None)
    if fallback is not None:
        return fallback
    return {
        "preset_name": "balanced",
        "vol_ratio_min": 0.75,
        "vol_ratio_max": 1.25,
        "range_pct_min": 0.50,
        "range_pct_max": 1.00,
        "price_action_max": 0.70,
    }


def handle_run_screening(date: str, preset: str = "balanced", feature_version: str = "v1") -> None:
    init_db()
    rows = get_feature_rows_by_date(trade_date=date, feature_version=feature_version)
    active_preset = _resolve_preset(preset)

    for features in rows:
        passed = is_fresh_ara_candidate(features, active_preset)
        score = score_candidate(features)
        pass_vol_ratio = 1 if active_preset["vol_ratio_min"] <= features["vol_ratio"] <= active_preset["vol_ratio_max"] else 0
        pass_range_pct = 1 if active_preset["range_pct_min"] <= features["range_pct"] <= active_preset["range_pct_max"] else 0
        pass_price_action = 1 if features["price_action"] < active_preset["price_action_max"] else 0
        pass_is_ara_t0 = 1 if int(features["is_ara_t0"]) == 0 else 0
        pass_count = pass_vol_ratio + pass_range_pct + pass_price_action + pass_is_ara_t0

        upsert_screening_result(
            screen_date=date,
            feature_date=date,
            ticker=features["ticker"],
            preset_name=preset,
            score=score,
            pass_vol_ratio=pass_vol_ratio,
            pass_range_pct=pass_range_pct,
            pass_price_action=pass_price_action,
            pass_is_ara_t0=pass_is_ara_t0,
            pass_count=pass_count,
            category="ideal" if passed else "candidate",
            reason_json=None,
        )


def handle_run_screening_range(start: str, end: str, preset: str = "balanced", feature_version: str = "v1") -> None:
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    if current > end_date:
        raise ValueError("start must be less than or equal to end")

    while current <= end_date:
        handle_run_screening(current.strftime("%Y-%m-%d"), preset, feature_version)
        current += timedelta(days=1)
