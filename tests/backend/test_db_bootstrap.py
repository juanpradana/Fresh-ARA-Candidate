from app.backend.core.db import init_db, SessionLocal
from app.backend.repositories.sqlite.models import Ticker


def test_init_db_creates_tables(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()
    session = SessionLocal()
    try:
        session.add(Ticker(ticker="BBCA.JK", symbol="BBCA.JK"))
        session.commit()
        assert session.query(Ticker).count() == 1
    finally:
        session.close()
