import csv
from io import StringIO

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
) -> dict:
    init_db()
    return {
        "data": get_backtest_summary(start=start, end=end, preset=preset),
        "meta": {
            "start": start,
            "end": end,
            "preset": preset,
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


@router.get("/screener")
def screener(
    screen_date: str | None = Query(default=None),
    preset: str = Query(default="balanced"),
) -> dict:
    init_db()
    rows = get_screener_rows(screen_date=screen_date, preset=preset)
    return {
        "data": rows,
        "meta": {
            "count": len(rows),
            "screen_date": screen_date,
            "preset": preset,
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
