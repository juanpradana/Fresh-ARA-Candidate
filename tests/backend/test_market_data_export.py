import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.backend.cli.commands.export_market_data import handle_export_market_data
from app.backend.core.db import Base
from app.backend.repositories.sqlite import repo
from app.backend.repositories.sqlite.models import PriceDaily


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
            source="yfinance",
            tickers=None,
            format="parquet",
        )

    assert "requires pyarrow" in str(exc.value)
