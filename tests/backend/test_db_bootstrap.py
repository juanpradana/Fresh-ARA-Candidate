from sqlalchemy import select

from app.backend.core.db import init_db, SessionLocal
from app.backend.repositories.sqlite.models import JobRun, Ticker


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


def test_job_runs_model_has_prd_columns(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()
    session = SessionLocal()
    try:
        session.add(
            JobRun(
                job_name="daily-screening",
                run_date="2026-05-09",
                status="running",
                error_message=None,
                started_at="2026-05-09T10:00:00",
                finished_at=None,
                rows_affected=0,
                meta_json="{}",
            )
        )
        session.commit()
        row = session.execute(select(JobRun).where(JobRun.run_date == "2026-05-09")).scalar_one()
        assert row.job_name == "daily-screening"
        assert row.rows_affected == 0
        assert row.meta_json == "{}"
    finally:
        session.close()
