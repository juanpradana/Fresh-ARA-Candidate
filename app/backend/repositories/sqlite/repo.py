from sqlalchemy import and_, func, select

from statistics import mean

from app.backend.core.db import SessionLocal
from app.backend.repositories.sqlite.models import FeatureDaily, JobRun, PriceDaily, ScreeningPreset, ScreeningResult, Ticker


def upsert_screening_result(
    screen_date: str,
    ticker: str,
    preset_name: str,
    score: float,
    pass_count: int,
    category: str,
    feature_date: str | None = None,
    pass_vol_ratio: int = 0,
    pass_range_pct: int = 0,
    pass_price_action: int = 0,
    pass_is_ara_t0: int = 0,
    reason_json: str | None = None,
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
            existing.feature_date = feature_date or screen_date
            existing.pass_vol_ratio = pass_vol_ratio
            existing.pass_range_pct = pass_range_pct
            existing.pass_price_action = pass_price_action
            existing.pass_is_ara_t0 = pass_is_ara_t0
            existing.pass_count = pass_count
            existing.category = category
            existing.reason_json = reason_json
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
                    feature_date=feature_date or screen_date,
                    ticker=ticker,
                    preset_name=preset_name,
                    score=score,
                    rank_num=1,
                    pass_vol_ratio=pass_vol_ratio,
                    pass_range_pct=pass_range_pct,
                    pass_price_action=pass_price_action,
                    pass_is_ara_t0=pass_is_ara_t0,
                    pass_count=pass_count,
                    category=category,
                    reason_json=reason_json,
                )
            )

        session.commit()
    finally:
        session.close()


def get_screener_rows(
    screen_date: str | None = None,
    preset: str = "balanced",
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    session = SessionLocal()
    try:
        stmt = select(ScreeningResult).where(ScreeningResult.preset_name == preset)
        if screen_date:
            stmt = stmt.where(ScreeningResult.screen_date == screen_date)
        stmt = stmt.order_by(ScreeningResult.rank_num.asc())
        if offset > 0:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

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


def get_screener_total(screen_date: str | None = None, preset: str = "balanced") -> int:
    session = SessionLocal()
    try:
        stmt = select(func.count(ScreeningResult.id)).where(ScreeningResult.preset_name == preset)
        if screen_date:
            stmt = stmt.where(ScreeningResult.screen_date == screen_date)
        total = session.execute(stmt).scalar_one()
        return int(total)
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

        feature_row = session.execute(
            select(FeatureDaily).where(
                FeatureDaily.trade_date == row.screen_date,
                FeatureDaily.ticker == row.ticker,
                FeatureDaily.feature_version == "v1",
            )
        ).scalar_one_or_none()

        preset_row = next(
            (item for item in get_default_presets() if item["preset_name"] == preset),
            get_default_presets()[1],
        )

        vol_ratio = feature_row.vol_ratio if feature_row is not None else None
        range_pct = feature_row.range_pct if feature_row is not None else None
        price_action = feature_row.price_action if feature_row is not None else None
        is_ara_t0 = feature_row.is_ara_t0 if feature_row is not None else None

        pass_vol_ratio = 1 if (
            vol_ratio is not None and preset_row["vol_ratio_min"] <= vol_ratio <= preset_row["vol_ratio_max"]
        ) else 0
        pass_range_pct = 1 if (
            range_pct is not None and preset_row["range_pct_min"] <= range_pct <= preset_row["range_pct_max"]
        ) else 0
        pass_price_action = 1 if (
            price_action is not None and price_action < preset_row["price_action_max"]
        ) else 0
        pass_is_ara_t0 = 1 if is_ara_t0 == 0 else 0

        return {
            "screen_date": row.screen_date,
            "ticker": row.ticker,
            "score": row.score,
            "rank_num": row.rank_num,
            "pass_count": row.pass_count,
            "category": row.category,
            "vol_ratio": vol_ratio,
            "range_pct": range_pct,
            "price_action": price_action,
            "is_ara_t0": is_ara_t0,
            "pass_vol_ratio": pass_vol_ratio,
            "pass_range_pct": pass_range_pct,
            "pass_price_action": pass_price_action,
            "pass_is_ara_t0": pass_is_ara_t0,
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

        feature_rows = session.execute(
            select(FeatureDaily).where(
                FeatureDaily.ticker == ticker,
                FeatureDaily.trade_date >= start,
                FeatureDaily.trade_date <= end,
                FeatureDaily.feature_version == "v1",
            )
        ).scalars().all()
        features_by_date = {feature_row.trade_date: feature_row for feature_row in feature_rows}

        enriched_rows: list[dict] = []
        for row in rows:
            feature_row = features_by_date.get(row.screen_date)
            preset_row = next(
                (item for item in get_default_presets() if item["preset_name"] == preset),
                get_default_presets()[1],
            )

            vol_ratio = feature_row.vol_ratio if feature_row is not None else None
            range_pct = feature_row.range_pct if feature_row is not None else None
            price_action = feature_row.price_action if feature_row is not None else None
            is_ara_t0 = feature_row.is_ara_t0 if feature_row is not None else None

            pass_vol_ratio = 1 if (
                vol_ratio is not None and preset_row["vol_ratio_min"] <= vol_ratio <= preset_row["vol_ratio_max"]
            ) else 0
            pass_range_pct = 1 if (
                range_pct is not None and preset_row["range_pct_min"] <= range_pct <= preset_row["range_pct_max"]
            ) else 0
            pass_price_action = 1 if (
                price_action is not None and price_action < preset_row["price_action_max"]
            ) else 0
            pass_is_ara_t0 = 1 if is_ara_t0 == 0 else 0

            enriched_rows.append(
                {
                    "screen_date": row.screen_date,
                    "ticker": row.ticker,
                    "score": row.score,
                    "rank_num": row.rank_num,
                    "pass_count": row.pass_count,
                    "category": row.category,
                    "vol_ratio": vol_ratio,
                    "range_pct": range_pct,
                    "price_action": price_action,
                    "is_ara_t0": is_ara_t0,
                    "pass_vol_ratio": pass_vol_ratio,
                    "pass_range_pct": pass_range_pct,
                    "pass_price_action": pass_price_action,
                    "pass_is_ara_t0": pass_is_ara_t0,
                }
            )

        return enriched_rows
    finally:
        session.close()


def _default_preset_seed_rows() -> list[dict]:
    return [
        {
            "preset_name": "conservative",
            "min_vol_ratio": 0.75,
            "max_vol_ratio": 1.25,
            "min_range_pct": 0.50,
            "max_range_pct": 0.90,
            "max_price_action": 0.50,
            "require_not_ara": 1,
            "score_weights_json": "{}",
            "is_default": 0,
        },
        {
            "preset_name": "balanced",
            "min_vol_ratio": 0.75,
            "max_vol_ratio": 1.25,
            "min_range_pct": 0.50,
            "max_range_pct": 1.00,
            "max_price_action": 0.70,
            "require_not_ara": 1,
            "score_weights_json": "{}",
            "is_default": 1,
        },
        {
            "preset_name": "aggressive",
            "min_vol_ratio": 0.70,
            "max_vol_ratio": 1.30,
            "min_range_pct": 0.50,
            "max_range_pct": 1.20,
            "max_price_action": 0.80,
            "require_not_ara": 1,
            "score_weights_json": "{}",
            "is_default": 0,
        },
    ]


def seed_default_presets() -> None:
    session = SessionLocal()
    try:
        for seed in _default_preset_seed_rows():
            existing = session.execute(
                select(ScreeningPreset).where(ScreeningPreset.preset_name == seed["preset_name"])
            ).scalar_one_or_none()
            if existing is None:
                session.add(ScreeningPreset(**seed))
        session.commit()
    finally:
        session.close()


def get_default_presets() -> list[dict]:
    session = SessionLocal()
    try:
        rows = session.execute(select(ScreeningPreset)).scalars().all()
        seed_order = {
            item["preset_name"]: idx for idx, item in enumerate(_default_preset_seed_rows())
        }
        rows.sort(key=lambda row: seed_order.get(row.preset_name, 999))
        if not rows:
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

        return [
            {
                "preset_name": row.preset_name,
                "vol_ratio_min": row.min_vol_ratio,
                "vol_ratio_max": row.max_vol_ratio,
                "range_pct_min": row.min_range_pct,
                "range_pct_max": row.max_range_pct,
                "price_action_max": row.max_price_action,
            }
            for row in rows
        ]
    finally:
        session.close()


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


def get_backtest_summary(start: str, end: str, preset: str, top_n: int | None = None) -> dict:
    session = SessionLocal()
    try:
        stmt = select(ScreeningResult).where(
            ScreeningResult.preset_name == preset,
            ScreeningResult.screen_date >= start,
            ScreeningResult.screen_date <= end,
        )
        stmt = stmt.order_by(ScreeningResult.score.desc())
        if top_n is not None:
            stmt = stmt.limit(top_n)

        rows = session.execute(stmt).scalars().all()

        total = len(rows)
        winners = sum(1 for row in rows if row.category == "ideal")
        avg_score = mean([row.score for row in rows]) if rows else 0.0

        precision_at_top_n = (winners / total) if total else 0.0
        return {
            "win_rate": (winners / total) if total else 0.0,
            "avg_score": avg_score,
            "total": total,
            "precision_at_top_n": precision_at_top_n,
        }
    finally:
        session.close()


def get_screener_csv_rows(screen_date: str | None, preset: str) -> list[dict]:
    return get_screener_rows(screen_date=screen_date, preset=preset)


def try_start_job_run(run_date: str, started_at: str) -> bool:
    session = SessionLocal()
    try:
        running = session.execute(
            select(JobRun).where(
                JobRun.job_name == "daily-screening",
                JobRun.status == "running",
                JobRun.finished_at.is_(None),
            )
        ).scalar_one_or_none()
        if running is not None:
            return False

        success = session.execute(
            select(JobRun).where(
                JobRun.job_name == "daily-screening",
                JobRun.run_date == run_date,
                JobRun.status == "success",
            )
        ).scalar_one_or_none()
        if success is not None:
            return False

        existing_running_for_date = session.execute(
            select(JobRun).where(
                JobRun.job_name == "daily-screening",
                JobRun.run_date == run_date,
                JobRun.status == "running",
            )
        ).scalar_one_or_none()
        if existing_running_for_date is not None:
            existing_running_for_date.error_message = None
            existing_running_for_date.started_at = started_at
            existing_running_for_date.finished_at = None
            session.commit()
            return True

        session.add(
            JobRun(
                job_name="daily-screening",
                run_date=run_date,
                status="running",
                error_message=None,
                started_at=started_at,
                finished_at=None,
                rows_affected=0,
                meta_json=None,
            )
        )
        session.commit()
        return True
    finally:
        session.close()


def _finish_job_run(
    run_date: str,
    finished_at: str,
    status: str,
    error_message: str | None,
    rows_affected: int = 0,
    meta_json: str | None = None,
) -> None:
    session = SessionLocal()
    try:
        running_row = session.execute(
            select(JobRun)
            .where(
                JobRun.job_name == "daily-screening",
                JobRun.run_date == run_date,
                JobRun.status == "running",
                JobRun.finished_at.is_(None),
            )
            .order_by(JobRun.id.desc())
        ).scalar_one_or_none()
        if running_row is None:
            return

        existing_terminal = session.execute(
            select(JobRun).where(
                JobRun.job_name == "daily-screening",
                JobRun.run_date == run_date,
                JobRun.status == status,
            )
        ).scalar_one_or_none()

        running_row.finished_at = finished_at
        running_row.rows_affected = rows_affected
        running_row.meta_json = meta_json

        if existing_terminal is not None:
            session.commit()
            return

        session.add(
            JobRun(
                job_name="daily-screening",
                run_date=run_date,
                status=status,
                error_message=error_message,
                started_at=running_row.started_at,
                finished_at=finished_at,
                rows_affected=rows_affected,
                meta_json=meta_json,
            )
        )
        session.commit()
    finally:
        session.close()


def finish_job_run_success(
    run_date: str,
    finished_at: str,
    rows_affected: int = 0,
    meta_json: str | None = None,
) -> None:
    _finish_job_run(
        run_date=run_date,
        finished_at=finished_at,
        status="success",
        error_message=None,
        rows_affected=rows_affected,
        meta_json=meta_json,
    )


def finish_job_run_failed(
    run_date: str,
    finished_at: str,
    error_message: str,
    rows_affected: int = 0,
    meta_json: str | None = None,
) -> None:
    _finish_job_run(
        run_date=run_date,
        finished_at=finished_at,
        status="failed",
        error_message=error_message,
        rows_affected=rows_affected,
        meta_json=meta_json,
    )


def finish_job_run_skipped(
    run_date: str,
    finished_at: str,
    message: str,
    rows_affected: int = 0,
    meta_json: str | None = None,
) -> None:
    _finish_job_run(
        run_date=run_date,
        finished_at=finished_at,
        status="skipped",
        error_message=message,
        rows_affected=rows_affected,
        meta_json=meta_json,
    )


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
                "job_name": row.job_name,
                "run_date": row.run_date,
                "status": row.status,
                "error_message": row.error_message,
                "started_at": row.started_at,
                "finished_at": row.finished_at,
                "rows_affected": row.rows_affected,
                "meta_json": row.meta_json,
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
