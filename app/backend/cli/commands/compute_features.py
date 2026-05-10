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
            days_since_last_ara=int(features["days_since_last_ara"]),
            is_bb_squeeze_20=int(features["is_bb_squeeze_20"]),
            daily_return_pct=float(features["daily_return_pct"]),
            vol_ratio_3d=float(features["vol_ratio_3d"]),
            vol_ratio_5d=float(features["vol_ratio_5d"]),
            vol_ratio_20=float(features["vol_ratio_20"]),
            cpr=float(features["cpr"]),
            range_volatility=float(features["range_volatility"]),
            bb_width=float(features["bb_width"]),
            price_vs_ma20_pct=float(features["price_vs_ma20_pct"]),
            price_vs_ma50_pct=float(features["price_vs_ma50_pct"]),
            value_traded=float(features["value_traded"]),
            rel_strength_5d_vs_jkse=float(features["rel_strength_5d_vs_jkse"]),
            float_shares=float(features["float_shares"]),
            shares_outstanding=float(features["shares_outstanding"]),
            float_ratio=float(features["float_ratio"]),
            consecutive_green_days=int(features["consecutive_green_days"]),
            rsi14=float(features["rsi14"]),
            rsi14_slope=float(features["rsi14_slope"]),
            atr5_atr20_ratio=float(features["atr5_atr20_ratio"]),
            dist_to_52w_high_pct=float(features["dist_to_52w_high_pct"]),
            is_ara_next_day=int(features["is_ara_next_day"]),
        )


def handle_compute_features_range(start: str, end: str, feature_version: str = "v1") -> None:
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    if current > end_date:
        raise ValueError("start must be less than or equal to end")

    while current <= end_date:
        handle_compute_features(current.strftime("%Y-%m-%d"), feature_version)
        current += timedelta(days=1)
