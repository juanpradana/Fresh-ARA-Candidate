from typing import Mapping


DEFAULT_BALANCED_PRESET = {
    "vol_ratio_min": 0.75,
    "vol_ratio_max": 1.25,
    "range_pct_min": 0.50,
    "range_pct_max": 1.00,
    "price_action_max": 0.70,
}


def passes_fresh_filter(days_since_last_ara: int) -> bool:
    return int(days_since_last_ara) >= 5


def is_fresh_ara_candidate(
    row: Mapping[str, float | int],
    preset: Mapping[str, float] | None = None,
) -> bool:
    active_preset = preset or DEFAULT_BALANCED_PRESET
    days_since_last_ara = int(row.get("days_since_last_ara", 999))
    return (
        float(active_preset["vol_ratio_min"]) <= float(row["vol_ratio"]) <= float(active_preset["vol_ratio_max"])
        and float(active_preset["range_pct_min"]) <= float(row["range_pct"]) <= float(active_preset["range_pct_max"])
        and float(row["price_action"]) < float(active_preset["price_action_max"])
        and int(row["is_ara_t0"]) == 0
        and passes_fresh_filter(days_since_last_ara)
    )
