from sqlalchemy import and_, func, select

from app.backend.core.db import SessionLocal
from app.backend.repositories.sqlite.models import ScreeningResult, Ticker


def upsert_screening_result(
    screen_date: str,
    ticker: str,
    preset_name: str,
    score: float,
    pass_count: int,
    category: str,
) -> None:
    session = SessionLocal()
    try:
        existing = session.execute(
            select(ScreeningResult).where(
                ScreeningResult.screen_date == screen_date,
                ScreeningResult.ticker == ticker,
                ScreeningResult.preset_name == preset_name,
            )
        ).scalar_one_or_none()

        if existing is not None:
            existing.score = score
            existing.pass_count = pass_count
            existing.category = category
            existing.rank_num = 1
        else:
            ticker_row = session.execute(
                select(Ticker).where(Ticker.ticker == ticker)
            ).scalar_one_or_none()
            if ticker_row is None:
                session.add(Ticker(ticker=ticker, symbol=ticker))

            session.add(
                ScreeningResult(
                    screen_date=screen_date,
                    ticker=ticker,
                    preset_name=preset_name,
                    score=score,
                    rank_num=1,
                    pass_count=pass_count,
                    category=category,
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


def get_latest_screen_date() -> str | None:
    session = SessionLocal()
    try:
        return session.execute(select(func.max(ScreeningResult.screen_date))).scalar_one_or_none()
    finally:
        session.close()


def get_screener_detail(ticker: str, screen_date: str | None, preset: str = "balanced") -> dict | None:
    session = SessionLocal()
    try:
        stmt = select(ScreeningResult).where(
            and_(
                ScreeningResult.ticker == ticker,
                ScreeningResult.preset_name == preset,
            )
        )
        if screen_date:
            stmt = stmt.where(ScreeningResult.screen_date == screen_date)
        else:
            latest = get_latest_screen_date()
            if latest is None:
                return None
            stmt = stmt.where(ScreeningResult.screen_date == latest)

        row = session.execute(stmt.order_by(ScreeningResult.rank_num.asc())).scalars().first()
        if row is None:
            return None
        return {
            "screen_date": row.screen_date,
            "ticker": row.ticker,
            "score": row.score,
            "rank_num": row.rank_num,
            "pass_count": row.pass_count,
            "category": row.category,
        }
    finally:
        session.close()


def get_screener_history(ticker: str, start: str, end: str, preset: str = "balanced") -> list[dict]:
    session = SessionLocal()
    try:
        stmt = (
            select(ScreeningResult)
            .where(
                and_(
                    ScreeningResult.ticker == ticker,
                    ScreeningResult.preset_name == preset,
                    ScreeningResult.screen_date >= start,
                    ScreeningResult.screen_date <= end,
                )
            )
            .order_by(ScreeningResult.screen_date.asc())
        )
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
