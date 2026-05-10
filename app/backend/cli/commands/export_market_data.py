import csv
from pathlib import Path

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_price_rows_for_export


FIELDNAMES = ["trade_date", "ticker", "open", "high", "low", "close", "volume", "source"]


def _write_csv(rows: list[dict], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
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
    source: str | None = None,
    tickers: str | None = None,
    format: str = "csv",
) -> None:
    init_db()
    ticker_list = None
    if tickers:
        ticker_list = [item.strip() for item in tickers.split(",") if item.strip()]

    rows = get_price_rows_for_export(
        date=date,
        start=start,
        end=end,
        source=source,
        tickers=ticker_list,
    )

    output_path = Path(output)
    if output_path.parent and str(output_path.parent) != ".":
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "csv":
        _write_csv(rows, output_path)
    elif format == "parquet":
        _write_parquet(rows, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")

    print(f"[EXPORT][OK] rows={len(rows)} format={format} output={output_path}")
