from sqlalchemy import select

from app.backend.core.db import SessionLocal
from app.backend.repositories.sqlite.models import ScreeningResult, Ticker


def seed_daily_result(screen_date: str) -> None:
    session = SessionLocal()
    try:
        exists = session.execute(
            select(ScreeningResult).where(
                ScreeningResult.screen_date == screen_date,
                ScreeningResult.ticker == "BBCA.JK",
                ScreeningResult.preset_name == "balanced",
            )
        ).scalar_one_or_none()
        if exists is not None:
            return

        ticker = session.execute(
            select(Ticker).where(Ticker.ticker == "BBCA.JK")
        ).scalar_one_or_none()
        if ticker is None:
            session.add(Ticker(ticker="BBCA.JK", symbol="BBCA.JK"))

        session.add(
            ScreeningResult(
                screen_date=screen_date,
                ticker="BBCA.JK",
                preset_name="balanced",
                score=0.91,
                rank_num=1,
                pass_count=4,
                category="ideal",
            )
        )
        session.commit()
    finally:
        session.close()


def get_screener_rows(screen_date: str | None = None, preset: str = "balanced") -> list[dict]:
    session = SessionLocal()
    try:
        stmt = select(ScreeningResult).where(ScreeningResult.preset_name == preset)
        if screen_date:
            stmt = stmt.where(ScreeningResult.screen_date == screen_date)
        stmt = stmt.order_by(ScreeningResult.rank_num.asc())

        rows = session.execute(stmt).scalars().all()
        return [
            {
                "screen_date": row.screen_date,
                "ticker": row.ticker,
                "score": row.score,
                "rank_num": row.rank_num,
                "pass_count": row.pass_count,
                "category": row.category,
            }
            for row in rows
        ]
    finally:
        session.close()
