from fastapi import APIRouter, Query

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import (
    get_latest_screen_date,
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
