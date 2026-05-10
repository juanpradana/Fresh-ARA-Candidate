import csv
from pathlib import Path

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_feature_rows_for_export, get_price_rows_for_export


PRICE_FIELDNAMES = ["trade_date", "ticker", "open", "high", "low", "close", "volume", "source"]
FEATURE_FIELDNAMES = [
    "trade_date",
    "ticker",
    "feature_version",
    "vol_ratio",
    "range_pct",
    "price_action",
    "is_ara_t0",
    "daily_return_pct",
    "vol_ratio_3d",
    "vol_ratio_5d",
    "vol_ratio_20",
    "cpr",
    "range_volatility",
    "bb_width",
    "is_bb_squeeze_20",
    "price_vs_ma20_pct",
    "price_vs_ma50_pct",
    "value_traded",
    "days_since_last_ara",
    "rel_strength_5d_vs_jkse",
    "float_shares",
    "shares_outstanding",
    "float_ratio",
    "consecutive_green_days",
    "rsi14",
    "rsi14_slope",
    "atr5_atr20_ratio",
    "dist_to_52w_high_pct",
    "is_ara_next_day",
]


def _write_csv(rows: list[dict], output_path: Path, fieldnames: list[str]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_parquet(rows: list[dict], output_path: Path) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Parquet export requires pyarrow. Install with: pip install pyarrow") from exc

    table = pa.Table.from_pylist(rows)
    pq.write_table(table, output_path)


def handle_export_market_data(
    date: str | None,
    start: str | None,
    end: str | None,
    output: str,
    dataset: str = "prices",
    source: str | None = None,
    tickers: str | None = None,
    feature_version: str = "v1",
    format: str = "csv",
) -> None:
    init_db()
    ticker_list = None
    if tickers:
        ticker_list = [item.strip() for item in tickers.split(",") if item.strip()]

    if dataset == "prices":
        rows = get_price_rows_for_export(
            date=date,
            start=start,
            end=end,
            source=source,
            tickers=ticker_list,
        )
        fieldnames = PRICE_FIELDNAMES
    elif dataset == "features":
        rows = get_feature_rows_for_export(
            date=date,
            start=start,
            end=end,
            tickers=ticker_list,
            feature_version=feature_version,
        )
        fieldnames = FEATURE_FIELDNAMES
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")

    output_path = Path(output)
    if output_path.parent and str(output_path.parent) != ".":
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "csv":
        _write_csv(rows, output_path, fieldnames)
    elif format == "parquet":
        _write_parquet(rows, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")

    print(f"[EXPORT][OK] dataset={dataset} rows={len(rows)} format={format} output={output_path}")
