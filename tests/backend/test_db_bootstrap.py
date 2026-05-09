from sqlalchemy import select, text

from app.backend.core.db import init_db, SessionLocal
from app.backend.repositories.sqlite.models import JobRun, ScreeningPreset, Ticker
from app.backend.repositories.sqlite.repo import (
    finish_job_run_failed,
    finish_job_run_success,
    try_start_job_run,
)


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


def test_try_start_job_run_blocks_when_another_run_is_running(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()
    session = SessionLocal()
    try:
        session.add(
            JobRun(
                job_name="daily-screening",
                run_date="2026-05-07",
                status="running",
                error_message=None,
                started_at="2026-05-07T10:00:00",
                finished_at=None,
                rows_affected=0,
                meta_json=None,
            )
        )
        session.commit()
    finally:
        session.close()

    started = try_start_job_run(run_date="2026-05-08", started_at="2026-05-08T10:00:00")
    assert started is False


def test_job_run_status_transition_creates_audit_rows(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()

    assert try_start_job_run(run_date="2026-05-07", started_at="2026-05-07T10:00:00") is True
    finish_job_run_failed(
        run_date="2026-05-07",
        finished_at="2026-05-07T10:05:00",
        error_message="simulated failure",
    )
    assert try_start_job_run(run_date="2026-05-07", started_at="2026-05-07T10:10:00") is True
    finish_job_run_success(
        run_date="2026-05-07",
        finished_at="2026-05-07T10:15:00",
    )

    session = SessionLocal()
    try:
        rows = session.execute(
            select(JobRun)
            .where(JobRun.run_date == "2026-05-07")
            .order_by(JobRun.id.asc())
        ).scalars().all()
        statuses = [row.status for row in rows]
        assert statuses == ["running", "failed", "success"]
    finally:
        session.close()


def test_job_runs_has_unique_key_for_job_date_status(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()

    session = SessionLocal()
    try:
        rows = session.execute(text("PRAGMA index_list(job_runs)")).all()
        index_names = {str(row[1]) for row in rows}
        unique_names = [row[1] for row in rows if int(row[2]) == 1]
        indexed_columns: list[set[str]] = []
        for name in unique_names:
            cols = session.execute(text(f"PRAGMA index_info({name})")).all()
            indexed_columns.append({str(col[2]) for col in cols})
        assert {"job_name", "run_date", "status"} in indexed_columns
        assert "idx_job_runs_name_date" in index_names
    finally:
        session.close()


def test_finish_job_run_failed_is_idempotent_for_same_status(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()

    assert try_start_job_run(run_date="2026-05-09", started_at="2026-05-09T10:00:00") is True
    finish_job_run_failed(
        run_date="2026-05-09",
        finished_at="2026-05-09T10:05:00",
        error_message="first",
    )
    finish_job_run_failed(
        run_date="2026-05-09",
        finished_at="2026-05-09T10:06:00",
        error_message="second",
    )

    session = SessionLocal()
    try:
        rows = session.execute(
            select(JobRun)
            .where(JobRun.run_date == "2026-05-09", JobRun.status == "failed")
            .order_by(JobRun.id.asc())
        ).scalars().all()
        assert len(rows) == 1
        assert rows[0].error_message == "first"
    finally:
        session.close()
