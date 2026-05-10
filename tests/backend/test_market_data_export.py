import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.backend.cli.commands.export_market_data import handle_export_market_data
from app.backend.core.db import Base
from app.backend.repositories.sqlite import repo
from app.backend.repositories.sqlite.models import FeatureDaily, PriceDaily


def test_get_price_rows_for_export_filters_by_range_source_and_tickers(monkeypatch):
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    test_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session_local, raising=False)

    session = test_session_local()
    try:
        session.add_all(
            [
                PriceDaily(
                    trade_date="2026-05-01",
                    ticker="BBCA.JK",
                    open=1.0,
                    high=2.0,
                    low=0.5,
                    close=1.5,
                    volume=100,
                    source="yfinance",
                ),
                PriceDaily(
                    trade_date="2026-05-02",
                    ticker="TLKM.JK",
                    open=2.0,
                    high=3.0,
                    low=1.5,
                    close=2.5,
                    volume=200,
                    source="yfinance",
                ),
                PriceDaily(
                    trade_date="2026-05-02",
                    ticker="ABCD.JK",
                    open=2.0,
                    high=3.0,
                    low=1.5,
                    close=2.5,
                    volume=200,
                    source="other",
                ),
            ]
        )
        session.commit()
    finally:
        session.close()

    rows = repo.get_price_rows_for_export(
        start="2026-05-01",
        end="2026-05-02",
        source="yfinance",
        tickers=["TLKM.JK"],
    )

    assert len(rows) == 1
    assert rows[0]["trade_date"] == "2026-05-02"
    assert rows[0]["ticker"] == "TLKM.JK"
    assert rows[0]["source"] == "yfinance"


def test_handle_export_market_data_writes_csv(monkeypatch, tmp_path):
    monkeypatch.setattr("app.backend.cli.commands.export_market_data.init_db", lambda: None, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.commands.export_market_data.get_price_rows_for_export",
        lambda date, start, end, source, tickers: [
            {
                "trade_date": "2026-05-01",
                "ticker": "BBCA.JK",
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 1.5,
                "volume": 100.0,
                "source": "yfinance",
            }
        ],
        raising=False,
    )

    output_path = tmp_path / "market.csv"
    handle_export_market_data(
        date="2026-05-01",
        start=None,
        end=None,
        output=str(output_path),
        source="yfinance",
        tickers="BBCA.JK",
        format="csv",
    )

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "trade_date,ticker,open,high,low,close,volume,source" in content
    assert "2026-05-01,BBCA.JK,1.0,2.0,0.5,1.5,100.0,yfinance" in content


def test_get_feature_rows_for_export_filters_by_range_version_and_tickers(monkeypatch):
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    test_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session_local, raising=False)

    session = test_session_local()
    try:
        session.add_all(
            [
                FeatureDaily(
                    trade_date="2026-05-01",
                    ticker="BBCA.JK",
                    vol_ratio=1.0,
                    range_pct=0.6,
                    price_action=0.2,
                    is_ara_t0=0,
                    feature_version="v2",
                    daily_return_pct=1.2,
                    vol_ratio_3d=1.1,
                    vol_ratio_5d=1.0,
                    vol_ratio_20=0.9,
                    cpr=100.0,
                    range_volatility=0.4,
                    bb_width=0.2,
                    is_bb_squeeze_20=1,
                    price_vs_ma20_pct=0.5,
                    price_vs_ma50_pct=0.7,
                    value_traded=1000.0,
                    days_since_last_ara=8,
                    rel_strength_5d_vs_jkse=0.3,
                    float_shares=50.0,
                    shares_outstanding=100.0,
                    float_ratio=0.5,
                    consecutive_green_days=3,
                    rsi14=54.0,
                    rsi14_slope=2.0,
                    atr5_atr20_ratio=0.6,
                    dist_to_52w_high_pct=-10.0,
                    is_ara_next_day=0,
                ),
                FeatureDaily(
                    trade_date="2026-05-02",
                    ticker="TLKM.JK",
                    vol_ratio=1.0,
                    range_pct=0.6,
                    price_action=0.2,
                    is_ara_t0=0,
                    feature_version="v2",
                    daily_return_pct=1.2,
                    vol_ratio_3d=1.1,
                    vol_ratio_5d=1.0,
                    vol_ratio_20=0.9,
                    cpr=100.0,
                    range_volatility=0.4,
                    bb_width=0.2,
                    is_bb_squeeze_20=1,
                    price_vs_ma20_pct=0.5,
                    price_vs_ma50_pct=0.7,
                    value_traded=1000.0,
                    days_since_last_ara=8,
                    rel_strength_5d_vs_jkse=0.3,
                    float_shares=50.0,
                    shares_outstanding=100.0,
                    float_ratio=0.5,
                    consecutive_green_days=4,
                    rsi14=55.0,
                    rsi14_slope=3.0,
                    atr5_atr20_ratio=0.5,
                    dist_to_52w_high_pct=-8.0,
                    is_ara_next_day=1,
                ),
                FeatureDaily(
                    trade_date="2026-05-02",
                    ticker="TLKM.JK",
                    vol_ratio=1.0,
                    range_pct=0.6,
                    price_action=0.2,
                    is_ara_t0=0,
                    feature_version="v1",
                ),
            ]
        )
        session.commit()
    finally:
        session.close()

    rows = repo.get_feature_rows_for_export(
        start="2026-05-01",
        end="2026-05-02",
        tickers=["TLKM.JK"],
        feature_version="v2",
    )

    assert len(rows) == 1
    assert rows[0]["trade_date"] == "2026-05-02"
    assert rows[0]["ticker"] == "TLKM.JK"
    assert rows[0]["feature_version"] == "v2"
    assert rows[0]["is_ara_next_day"] == 1


def test_handle_export_market_data_writes_features_csv(monkeypatch, tmp_path):
    monkeypatch.setattr("app.backend.cli.commands.export_market_data.init_db", lambda: None, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.commands.export_market_data.get_feature_rows_for_export",
        lambda date, start, end, tickers, feature_version: [
            {
                "trade_date": "2026-05-01",
                "ticker": "BBCA.JK",
                "feature_version": "v2",
                "vol_ratio": 1.0,
                "range_pct": 0.6,
                "price_action": 0.2,
                "is_ara_t0": 0,
                "daily_return_pct": 1.2,
                "vol_ratio_3d": 1.1,
                "vol_ratio_5d": 1.0,
                "vol_ratio_20": 0.9,
                "cpr": 100.0,
                "range_volatility": 0.4,
                "bb_width": 0.2,
                "is_bb_squeeze_20": 1,
                "price_vs_ma20_pct": 0.5,
                "price_vs_ma50_pct": 0.7,
                "value_traded": 1000.0,
                "days_since_last_ara": 8,
                "rel_strength_5d_vs_jkse": 0.3,
                "float_shares": 50.0,
                "shares_outstanding": 100.0,
                "float_ratio": 0.5,
                "consecutive_green_days": 4,
                "rsi14": 55.0,
                "rsi14_slope": 3.0,
                "atr5_atr20_ratio": 0.5,
                "dist_to_52w_high_pct": -8.0,
                "is_ara_next_day": 0,
            }
        ],
        raising=False,
    )

    output_path = tmp_path / "features.csv"
    handle_export_market_data(
        date="2026-05-01",
        start=None,
        end=None,
        output=str(output_path),
        dataset="features",
        source=None,
        tickers="BBCA.JK",
        feature_version="v2",
        format="csv",
    )

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "trade_date,ticker,feature_version,vol_ratio,range_pct,price_action,is_ara_t0,daily_return_pct,vol_ratio_3d,vol_ratio_5d,vol_ratio_20,cpr,range_volatility,bb_width,is_bb_squeeze_20,price_vs_ma20_pct,price_vs_ma50_pct,value_traded,days_since_last_ara,rel_strength_5d_vs_jkse,float_shares,shares_outstanding,float_ratio,consecutive_green_days,rsi14,rsi14_slope,atr5_atr20_ratio,dist_to_52w_high_pct,is_ara_next_day" in content
    assert "2026-05-01,BBCA.JK,v2,1.0,0.6,0.2,0,1.2,1.1,1.0,0.9,100.0,0.4,0.2,1,0.5,0.7,1000.0,8,0.3,50.0,100.0,0.5,4,55.0,3.0,0.5,-8.0,0" in content


def test_handle_export_market_data_raises_when_pyarrow_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("app.backend.cli.commands.export_market_data.init_db", lambda: None, raising=False)
    monkeypatch.setattr(
        "app.backend.cli.commands.export_market_data.get_price_rows_for_export",
        lambda date, start, end, source, tickers: [],
        raising=False,
    )

    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("pyarrow"):
            raise ImportError("missing pyarrow")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import, raising=False)

    with pytest.raises(RuntimeError) as exc:
        handle_export_market_data(
            date="2026-05-01",
            start=None,
            end=None,
            output=str(tmp_path / "market.parquet"),
            dataset="prices",
            source="yfinance",
            tickers=None,
            feature_version="v1",
            format="parquet",
        )

    assert "requires pyarrow" in str(exc.value)
