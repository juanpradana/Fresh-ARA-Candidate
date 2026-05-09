from sqlalchemy import Column, Float, Integer, Text, UniqueConstraint

from app.backend.core.db import Base


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(Text, unique=True, nullable=False)
    symbol = Column(Text, nullable=False)


class PriceDaily(Base):
    __tablename__ = "prices_daily"
    __table_args__ = (UniqueConstraint("trade_date", "ticker", name="uq_prices_daily_trade_ticker"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(Text, nullable=False)
    ticker = Column(Text, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    source = Column(Text, nullable=False, default="yfinance")


class FeatureDaily(Base):
    __tablename__ = "features_daily"
    __table_args__ = (UniqueConstraint("trade_date", "ticker", "feature_version", name="uq_features_daily_trade_ticker_version"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(Text, nullable=False)
    ticker = Column(Text, nullable=False)
    vol_ratio = Column(Float, nullable=False)
    range_pct = Column(Float, nullable=False)
    price_action = Column(Float, nullable=False)
    is_ara_t0 = Column(Integer, nullable=False, default=0)
    feature_version = Column(Text, nullable=False, default="v1")


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screen_date = Column(Text, nullable=False)
    feature_date = Column(Text, nullable=False, default="")
    ticker = Column(Text, nullable=False)
    preset_name = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    rank_num = Column(Integer, nullable=False)
    pass_vol_ratio = Column(Integer, nullable=False, default=0)
    pass_range_pct = Column(Integer, nullable=False, default=0)
    pass_price_action = Column(Integer, nullable=False, default=0)
    pass_is_ara_t0 = Column(Integer, nullable=False, default=0)
    pass_count = Column(Integer, nullable=False)
    category = Column(Text, nullable=False)
    reason_json = Column(Text, nullable=True)


class ScreeningPreset(Base):
    __tablename__ = "screening_presets"

    preset_name = Column(Text, primary_key=True)
    min_vol_ratio = Column(Float, nullable=False)
    max_vol_ratio = Column(Float, nullable=False)
    min_range_pct = Column(Float, nullable=False)
    max_range_pct = Column(Float, nullable=False)
    max_price_action = Column(Float, nullable=False)
    require_not_ara = Column(Integer, nullable=False, default=1)
    score_weights_json = Column(Text, nullable=False, default="{}")
    is_default = Column(Integer, nullable=False, default=0)
    updated_at = Column(Text, nullable=True)


class JobRun(Base):
    __tablename__ = "job_runs"
    __table_args__ = (UniqueConstraint("job_name", "run_date", "status", name="uq_job_runs_name_date_status"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(Text, nullable=False, default="daily-screening")
    run_date = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    error_message = Column(Text, nullable=True)
    started_at = Column(Text, nullable=False)
    finished_at = Column(Text, nullable=True)
    rows_affected = Column(Integer, nullable=False, default=0)
    meta_json = Column(Text, nullable=True)


class Watchlist(Base):
    __tablename__ = "watchlists"
    __table_args__ = (UniqueConstraint("watchlist_name", "ticker", name="uq_watchlists_name_ticker"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist_name = Column(Text, nullable=False)
    ticker = Column(Text, nullable=False)


class AlertEvent(Base):
    __tablename__ = "alert_events"
    __table_args__ = (
        UniqueConstraint("run_date", "watchlist_name", "ticker", "preset", name="uq_alert_events_run_watchlist_ticker_preset"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_date = Column(Text, nullable=False)
    watchlist_name = Column(Text, nullable=False)
    ticker = Column(Text, nullable=False)
    preset = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)


class KpiDailySnapshot(Base):
    __tablename__ = "kpi_daily_snapshots"
    __table_args__ = (UniqueConstraint("run_date", "preset", name="uq_kpi_daily_run_preset"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_date = Column(Text, nullable=False)
    preset = Column(Text, nullable=False)
    precision_at_top_n = Column(Float, nullable=False, default=0.0)
    screener_views = Column(Integer, nullable=False, default=0)
    alerts_views = Column(Integer, nullable=False, default=0)
    watchlist_views = Column(Integer, nullable=False, default=0)
    created_at = Column(Text, nullable=False)
