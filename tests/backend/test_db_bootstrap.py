from sqlalchemy import select

from app.backend.core.db import init_db, SessionLocal
from app.backend.repositories.sqlite.models import JobRun, ScreeningPreset, Ticker


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


def test_screening_results_model_has_prd_columns(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()
    session = SessionLocal()
    try:
        from app.backend.repositories.sqlite.models import ScreeningResult

        session.add(
            ScreeningResult(
                screen_date="2026-05-09",
                feature_date="2026-05-09",
                ticker="BBCA.JK",
                preset_name="balanced",
                score=0.91,
                rank_num=1,
                pass_vol_ratio=1,
                pass_range_pct=1,
                pass_price_action=1,
                pass_is_ara_t0=1,
                pass_count=4,
                category="ideal",
                reason_json='{"rule":"balanced"}',
            )
        )
        session.commit()
        row = session.execute(select(ScreeningResult).where(ScreeningResult.ticker == "BBCA.JK")).scalar_one()
        assert row.feature_date == "2026-05-09"
        assert row.pass_vol_ratio == 1
        assert row.pass_range_pct == 1
        assert row.pass_price_action == 1
        assert row.pass_is_ara_t0 == 1
        assert row.reason_json == '{"rule":"balanced"}'
    finally:
        session.close()


def test_screening_presets_seeded_in_db(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()
    session = SessionLocal()
    try:
        rows = session.execute(select(ScreeningPreset).order_by(ScreeningPreset.preset_name.asc())).scalars().all()
        names = {row.preset_name for row in rows}
        assert {"conservative", "balanced", "aggressive"}.issubset(names)
        balanced = next(row for row in rows if row.preset_name == "balanced")
        assert balanced.min_vol_ratio == 0.75
        assert balanced.max_vol_ratio == 1.25
        assert balanced.min_range_pct == 0.50
        assert balanced.max_range_pct == 1.00
        assert balanced.max_price_action == 0.70
        assert balanced.require_not_ara == 1
    finally:
        session.close()
