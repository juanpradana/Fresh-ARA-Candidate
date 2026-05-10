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


def _passes_legacy(
    row: Mapping[str, float | int],
    preset: Mapping[str, float],
) -> bool:
    days_since_last_ara = int(row.get("days_since_last_ara", 999))
    return (
        float(preset["vol_ratio_min"]) <= float(row["vol_ratio"]) <= float(preset["vol_ratio_max"])
        and float(preset["range_pct_min"]) <= float(row["range_pct"]) <= float(preset["range_pct_max"])
        and float(row["price_action"]) < float(preset["price_action_max"])
        and int(row["is_ara_t0"]) == 0
        and passes_fresh_filter(days_since_last_ara)
    )


def _passes_rich_v1(
    row: Mapping[str, float | int],
    preset: Mapping[str, float],
) -> bool:
    if not _passes_legacy(row, preset):
        return False

    return (
        float(row.get("vol_ratio_3d", row["vol_ratio"])) > 0.0
        and float(row.get("vol_ratio_5d", row["vol_ratio"])) > 0.0
        and float(row.get("vol_ratio_20", row["vol_ratio"])) > 0.0
        and float(row.get("value_traded", 0.0)) > 0.0
        and float(row.get("float_ratio", 0.0)) > 0.0
        and float(row.get("rel_strength_5d_vs_jkse", 0.0)) >= 0.0
    )


def is_fresh_ara_candidate(
    row: Mapping[str, float | int],
    preset: Mapping[str, float] | None = None,
    feature_set: str = "legacy",
) -> bool:
    active_preset = preset or DEFAULT_BALANCED_PRESET
    if feature_set == "rich_v1":
        return _passes_rich_v1(row, active_preset)
    return _passes_legacy(row, active_preset)
