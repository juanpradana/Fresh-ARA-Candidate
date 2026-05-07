from sqlalchemy import and_, func, select

from statistics import mean

from app.backend.core.db import SessionLocal
from app.backend.repositories.sqlite.models import FeatureDaily, JobRun, PriceDaily, ScreeningResult, Ticker


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


def get_default_presets() -> list[dict]:
    return [
        {
            "preset_name": "conservative",
            "vol_ratio_min": 0.75,
            "vol_ratio_max": 1.25,
            "range_pct_min": 0.50,
            "range_pct_max": 0.90,
            "price_action_max": 0.50,
        },
        {
            "preset_name": "balanced",
            "vol_ratio_min": 0.75,
            "vol_ratio_max": 1.25,
            "range_pct_min": 0.50,
            "range_pct_max": 1.00,
            "price_action_max": 0.70,
        },
        {
            "preset_name": "aggressive",
            "vol_ratio_min": 0.70,
            "vol_ratio_max": 1.30,
            "range_pct_min": 0.50,
            "range_pct_max": 1.20,
            "price_action_max": 0.80,
        },
    ]


def get_distribution(screen_date: str, preset: str) -> dict:
    session = SessionLocal()
    try:
        rows = session.execute(
            select(ScreeningResult).where(
                ScreeningResult.screen_date == screen_date,
                ScreeningResult.preset_name == preset,
            )
        ).scalars().all()

        by_category: dict[str, int] = {}
        by_pass_count: dict[str, int] = {}

        for row in rows:
            by_category[row.category] = by_category.get(row.category, 0) + 1
            key = str(row.pass_count)
            by_pass_count[key] = by_pass_count.get(key, 0) + 1

        return {
            "by_category": by_category,
            "by_pass_count": by_pass_count,
            "total": len(rows),
        }
    finally:
        session.close()


def get_backtest_summary(start: str, end: str, preset: str) -> dict:
    session = SessionLocal()
    try:
        rows = session.execute(
            select(ScreeningResult).where(
                ScreeningResult.preset_name == preset,
                ScreeningResult.screen_date >= start,
                ScreeningResult.screen_date <= end,
            )
        ).scalars().all()

        total = len(rows)
        winners = sum(1 for row in rows if row.category == "ideal")
        avg_score = mean([row.score for row in rows]) if rows else 0.0

        return {
            "win_rate": (winners / total) if total else 0.0,
            "avg_score": avg_score,
            "total": total,
        }
    finally:
        session.close()


def get_screener_csv_rows(screen_date: str | None, preset: str) -> list[dict]:
    return get_screener_rows(screen_date=screen_date, preset=preset)


def try_start_job_run(run_date: str, started_at: str) -> bool:
    session = SessionLocal()
    try:
        existing = session.execute(
            select(JobRun).where(JobRun.run_date == run_date)
        ).scalar_one_or_none()
        if existing is not None:
            return False

        session.add(
            JobRun(
                run_date=run_date,
                status="running",
                error_message=None,
                started_at=started_at,
                finished_at=None,
            )
        )
        session.commit()
        return True
    finally:
        session.close()


def finish_job_run_success(run_date: str, finished_at: str) -> None:
    session = SessionLocal()
    try:
        row = session.execute(
            select(JobRun).where(JobRun.run_date == run_date)
        ).scalar_one_or_none()
        if row is None:
            return
        row.status = "success"
        row.error_message = None
        row.finished_at = finished_at
        session.commit()
    finally:
        session.close()


def finish_job_run_failed(run_date: str, finished_at: str, error_message: str) -> None:
    session = SessionLocal()
    try:
        row = session.execute(
            select(JobRun).where(JobRun.run_date == run_date)
        ).scalar_one_or_none()
        if row is None:
            return
        row.status = "failed"
        row.error_message = error_message
        row.finished_at = finished_at
        session.commit()
    finally:
        session.close()


def get_recent_job_runs(limit: int = 10) -> list[dict]:
    session = SessionLocal()
    try:
        rows = session.execute(
            select(JobRun)
            .order_by(JobRun.started_at.desc())
            .limit(limit)
        ).scalars().all()
        return [
            {
                "run_date": row.run_date,
                "status": row.status,
                "error_message": row.error_message,
                "started_at": row.started_at,
                "finished_at": row.finished_at,
            }
            for row in rows
        ]
    finally:
        session.close()


def has_price_daily(trade_date: str, ticker: str) -> bool:
    session = SessionLocal()
    try:
        row = session.execute(
            select(PriceDaily).where(
                PriceDaily.trade_date == trade_date,
                PriceDaily.ticker == ticker,
            )
        ).scalar_one_or_none()
        return row is not None
    finally:
        session.close()


def get_missing_tickers_for_date(trade_date: str, tickers: list[str]) -> list[str]:
    if not tickers:
        return []

    session = SessionLocal()
    try:
        rows = session.execute(
            select(PriceDaily.ticker).where(PriceDaily.trade_date == trade_date)
        ).all()
        existing = {ticker for (ticker,) in rows}
        return [ticker for ticker in tickers if ticker not in existing]
    finally:
        session.close()


def upsert_price_daily(
    trade_date: str,
    ticker: str,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    volume: float,
    source: str = "yfinance",
) -> None:
    session = SessionLocal()
    try:
        existing = session.execute(
            select(PriceDaily).where(
                PriceDaily.trade_date == trade_date,
                PriceDaily.ticker == ticker,
            )
        ).scalar_one_or_none()

        if existing is None:
            session.add(
                PriceDaily(
                    trade_date=trade_date,
                    ticker=ticker,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                    source=source,
                )
            )
        else:
            existing.open = open_price
            existing.high = high_price
            existing.low = low_price
            existing.close = close_price
            existing.volume = volume
            existing.source = source

        session.commit()
    finally:
        session.close()


def get_price_rows_by_date(trade_date: str) -> list[dict]:
    session = SessionLocal()
    try:
        rows = session.execute(
            select(PriceDaily)
            .where(PriceDaily.trade_date == trade_date)
            .order_by(PriceDaily.ticker.asc())
        ).scalars().all()
        return [
            {
                "ticker": row.ticker,
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume,
                "prev_volume": row.volume,
                "prev_close": row.close,
            }
            for row in rows
        ]
    finally:
        session.close()


def upsert_feature_daily(
    trade_date: str,
    ticker: str,
    vol_ratio: float,
    range_pct: float,
    price_action: float,
    is_ara_t0: int,
    feature_version: str = "v1",
) -> None:
    session = SessionLocal()
    try:
        existing = session.execute(
            select(FeatureDaily).where(
                FeatureDaily.trade_date == trade_date,
                FeatureDaily.ticker == ticker,
                FeatureDaily.feature_version == feature_version,
            )
        ).scalar_one_or_none()

        if existing is None:
            session.add(
                FeatureDaily(
                    trade_date=trade_date,
                    ticker=ticker,
                    vol_ratio=vol_ratio,
                    range_pct=range_pct,
                    price_action=price_action,
                    is_ara_t0=is_ara_t0,
                    feature_version=feature_version,
                )
            )
        else:
            existing.vol_ratio = vol_ratio
            existing.range_pct = range_pct
            existing.price_action = price_action
            existing.is_ara_t0 = is_ara_t0

        session.commit()
    finally:
        session.close()


def get_feature_rows_by_date(trade_date: str, feature_version: str = "v1") -> list[dict]:
    session = SessionLocal()
    try:
        rows = session.execute(
            select(FeatureDaily)
            .where(
                FeatureDaily.trade_date == trade_date,
                FeatureDaily.feature_version == feature_version,
            )
            .order_by(FeatureDaily.ticker.asc())
        ).scalars().all()
        return [
            {
                "ticker": row.ticker,
                "vol_ratio": row.vol_ratio,
                "range_pct": row.range_pct,
                "price_action": row.price_action,
                "is_ara_t0": row.is_ara_t0,
            }
            for row in rows
        ]
    finally:
        session.close()
