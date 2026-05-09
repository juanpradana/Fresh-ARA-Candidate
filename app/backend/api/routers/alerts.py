from fastapi import APIRouter, Query

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import list_alert_events

router = APIRouter()


@router.get("/alerts/recent")
def recent_alerts(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    init_db()
    rows = list_alert_events(limit=limit)
    return {
        "data": rows,
        "meta": {
            "limit": limit,
            "count": len(rows),
        },
        "error": None,
    }
