import csv
from io import BytesIO, StringIO

from openpyxl import Workbook

from fastapi import APIRouter, Query, Response

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import (
    get_backtest_summary,
    get_default_presets,
    get_distribution,
    get_latest_screen_date,
    get_recent_job_runs,
    get_screener_csv_rows,
    get_screener_detail,
    get_screener_history,
    get_screener_rows,
)

router = APIRouter()


@router.get("/meta/latest-screen-date")
def latest_screen_date() -> dict:
    init_db()
    latest = get_latest_screen_date()
    return {
        "data": {
            "latest_screen_date": latest,
        },
        "meta": {},
        "error": None,
    }


@router.get("/meta/data-freshness")
def data_freshness() -> dict:
    init_db()
    latest = get_latest_screen_date()
    return {
        "data": {
            "latest_screen_date": latest,
            "is_complete": latest is not None,
            "warning": None if latest is not None else "Data EOD belum complete",
        },
        "meta": {},
        "error": None,
    }


@router.get("/meta/presets")
def presets() -> dict:
    return {
        "data": get_default_presets(),
        "meta": {},
        "error": None,
    }


@router.get("/meta/job-runs")
def meta_job_runs(limit: int = Query(default=10, ge=1, le=100)) -> dict:
    init_db()
    rows = get_recent_job_runs(limit=limit)
    return {
        "data": rows,
        "meta": {
            "count": len(rows),
            "limit": limit,
        },
        "error": None,
    }


@router.get("/analytics/distribution")
def analytics_distribution(
    screen_date: str = Query(...),
    preset: str = Query(default="balanced"),
) -> dict:
    init_db()
    return {
        "data": get_distribution(screen_date=screen_date, preset=preset),
        "meta": {
            "screen_date": screen_date,
            "preset": preset,
        },
        "error": None,
    }


@router.get("/analytics/backtest")
def analytics_backtest(
    start: str = Query(...),
    end: str = Query(...),
    preset: str = Query(default="balanced"),
    top_n: int | None = Query(default=None, ge=1),
) -> dict:
    init_db()
    return {
        "data": get_backtest_summary(start=start, end=end, preset=preset, top_n=top_n),
        "meta": {
            "start": start,
            "end": end,
            "preset": preset,
            "top_n": top_n,
        },
        "error": None,
    }


@router.get("/export/screener.csv")
def export_screener_csv(
    screen_date: str | None = Query(default=None),
    preset: str = Query(default="balanced"),
) -> Response:
    init_db()
    rows = get_screener_csv_rows(screen_date=screen_date, preset=preset)
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["screen_date", "ticker", "score", "rank_num", "pass_count", "category"],
    )
    writer.writeheader()
    writer.writerows(rows)
    return Response(content=output.getvalue(), media_type="text/csv")


@router.get("/export/screener.xlsx")
def export_screener_xlsx(
    screen_date: str | None = Query(default=None),
    preset: str = Query(default="balanced"),
) -> Response:
    init_db()
    rows = get_screener_csv_rows(screen_date=screen_date, preset=preset)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Screener"
    headers = ["screen_date", "ticker", "score", "rank_num", "pass_count", "category"]
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header) for header in headers])

    output = BytesIO()
    workbook.save(output)
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/screener")
def screener(
    screen_date: str | None = Query(default=None),
    preset: str = Query(default="balanced"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    init_db()
    rows = get_screener_rows(screen_date=screen_date, preset=preset, limit=limit, offset=offset)
    return {
        "data": rows,
        "meta": {
            "count": len(rows),
            "screen_date": screen_date,
            "preset": preset,
            "limit": limit,
            "offset": offset,
        },
        "error": None,
    }


@router.get("/screener/{ticker}")
def screener_detail(
    ticker: str,
    screen_date: str | None = Query(default=None),
    preset: str = Query(default="balanced"),
) -> dict:
    init_db()
    detail = get_screener_detail(ticker=ticker, screen_date=screen_date, preset=preset)
    return {
        "data": detail,
        "meta": {
            "screen_date": screen_date,
            "preset": preset,
        },
        "error": None,
    }


@router.get("/screener/{ticker}/history")
def screener_history(
    ticker: str,
    start: str = Query(...),
    end: str = Query(...),
    preset: str = Query(default="balanced"),
) -> dict:
    init_db()
    rows = get_screener_history(ticker=ticker, start=start, end=end, preset=preset)
    return {
        "data": rows,
        "meta": {
            "start": start,
            "end": end,
            "preset": preset,
        },
        "error": None,
    }
