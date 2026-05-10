from datetime import datetime, timedelta

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_price_rows_by_date, upsert_feature_daily
from app.backend.services.feature_engineering.service import compute_features


def handle_compute_features(date: str, feature_version: str = "v1") -> None:
    init_db()
    rows = get_price_rows_by_date(trade_date=date)

    for row in rows:
        features = compute_features(row)
        upsert_feature_daily(
            trade_date=date,
            ticker=row["ticker"],
            vol_ratio=features["vol_ratio"],
            range_pct=features["range_pct"],
            price_action=features["price_action"],
            is_ara_t0=int(features["is_ara_t0"]),
            feature_version=feature_version,
        )


def handle_compute_features_range(start: str, end: str, feature_version: str = "v1") -> None:
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    if current > end_date:
        raise ValueError("start must be less than or equal to end")

    while current <= end_date:
        handle_compute_features(current.strftime("%Y-%m-%d"), feature_version)
        current += timedelta(days=1)
