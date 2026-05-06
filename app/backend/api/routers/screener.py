from fastapi import APIRouter, Query

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import get_screener_rows

router = APIRouter()


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
