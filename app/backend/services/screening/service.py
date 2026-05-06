from typing import Mapping


def is_fresh_ara_candidate(row: Mapping[str, float | int]) -> bool:
    return (
        0.75 <= float(row["vol_ratio"]) <= 1.25
        and 0.50 <= float(row["range_pct"]) <= 1.00
        and float(row["price_action"]) < 0.70
        and int(row["is_ara_t0"]) == 0
    )
