from fastapi import APIRouter
from pydantic import BaseModel

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import (
    add_watchlist_ticker,
    list_watchlist_tickers,
    list_watchlists,
    remove_watchlist_ticker,
)

router = APIRouter()


class WatchlistTickerPayload(BaseModel):
    ticker: str


@router.get("/watchlists")
def watchlists() -> dict:
    init_db()
    return {
        "data": list_watchlists(),
        "meta": {},
        "error": None,
    }


@router.get("/watchlists/{watchlist_name}/tickers")
def watchlist_tickers(watchlist_name: str) -> dict:
    init_db()
    return {
        "data": list_watchlist_tickers(watchlist_name=watchlist_name),
        "meta": {"watchlist_name": watchlist_name},
        "error": None,
    }


@router.post("/watchlists/{watchlist_name}/tickers")
def watchlist_add_ticker(watchlist_name: str, payload: WatchlistTickerPayload) -> dict:
    init_db()
    row = add_watchlist_ticker(watchlist_name=watchlist_name, ticker=payload.ticker)
    return {
        "data": row,
        "meta": {"watchlist_name": watchlist_name},
        "error": None,
    }


@router.delete("/watchlists/{watchlist_name}/tickers/{ticker}")
def watchlist_delete_ticker(watchlist_name: str, ticker: str) -> dict:
    init_db()
    removed = remove_watchlist_ticker(watchlist_name=watchlist_name, ticker=ticker)
    return {
        "data": {
            "watchlist_name": watchlist_name,
            "ticker": ticker,
            "removed": removed,
        },
        "meta": {"watchlist_name": watchlist_name},
        "error": None,
    }
