from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.backend.core.config import settings

Base = declarative_base()
engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def _database_url() -> str:
    db_path = Path(settings.app_db_path)
    if db_path.parent and str(db_path.parent) != ".":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


def _ensure_job_runs_columns(bind_engine: Engine) -> None:
    required_columns = {
        "job_name": "TEXT NOT NULL DEFAULT 'daily-screening'",
        "rows_affected": "INTEGER NOT NULL DEFAULT 0",
        "meta_json": "TEXT",
    }

    with bind_engine.begin() as connection:
        rows = connection.exec_driver_sql("PRAGMA table_info(job_runs)").fetchall()
        if not rows:
            return
        existing = {str(row[1]) for row in rows}
        for column_name, column_ddl in required_columns.items():
            if column_name in existing:
                continue
            connection.exec_driver_sql(f"ALTER TABLE job_runs ADD COLUMN {column_name} {column_ddl}")


def _ensure_screening_results_columns(bind_engine: Engine) -> None:
    required_columns = {
        "feature_date": "TEXT NOT NULL DEFAULT ''",
        "pass_vol_ratio": "INTEGER NOT NULL DEFAULT 0",
        "pass_range_pct": "INTEGER NOT NULL DEFAULT 0",
        "pass_price_action": "INTEGER NOT NULL DEFAULT 0",
        "pass_is_ara_t0": "INTEGER NOT NULL DEFAULT 0",
        "reason_json": "TEXT",
    }

    with bind_engine.begin() as connection:
        rows = connection.exec_driver_sql("PRAGMA table_info(screening_results)").fetchall()
        if not rows:
            return
        existing = {str(row[1]) for row in rows}
        for column_name, column_ddl in required_columns.items():
            if column_name in existing:
                continue
            connection.exec_driver_sql(f"ALTER TABLE screening_results ADD COLUMN {column_name} {column_ddl}")


def _ensure_job_runs_unique_key(bind_engine: Engine) -> None:
    with bind_engine.begin() as connection:
        rows = connection.exec_driver_sql("PRAGMA table_info(job_runs)").fetchall()
        if not rows:
            return

        indexes = connection.exec_driver_sql("PRAGMA index_list(job_runs)").fetchall()
        unique_columns: list[set[str]] = []
        for row in indexes:
            if int(row[2]) != 1:
                continue
            index_name = str(row[1])
            cols = connection.exec_driver_sql(f"PRAGMA index_info({index_name})").fetchall()
            unique_columns.append({str(col[2]) for col in cols})

        if {"job_name", "run_date", "status"} in unique_columns:
            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_job_runs_name_date ON job_runs (job_name, run_date)"
            )
            return

        connection.exec_driver_sql(
            """
            CREATE TABLE job_runs_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT NOT NULL DEFAULT 'daily-screening',
                run_date TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                rows_affected INTEGER NOT NULL DEFAULT 0,
                meta_json TEXT,
                UNIQUE (job_name, run_date, status)
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO job_runs_new (
                id, job_name, run_date, status, error_message, started_at, finished_at, rows_affected, meta_json
            )
            SELECT
                jr.id,
                jr.job_name,
                jr.run_date,
                jr.status,
                jr.error_message,
                jr.started_at,
                jr.finished_at,
                jr.rows_affected,
                jr.meta_json
            FROM job_runs jr
            JOIN (
                SELECT MAX(id) AS max_id
                FROM job_runs
                GROUP BY job_name, run_date, status
            ) dedup ON dedup.max_id = jr.id
            """
        )
        connection.exec_driver_sql("DROP TABLE job_runs")
        connection.exec_driver_sql("ALTER TABLE job_runs_new RENAME TO job_runs")
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_job_runs_name_date ON job_runs (job_name, run_date)"
        )


def init_db() -> None:
    from app.backend.repositories.sqlite import models
    from app.backend.repositories.sqlite.repo import seed_default_presets

    global engine
    engine = create_engine(_database_url(), future=True)
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    _ensure_job_runs_columns(engine)
    _ensure_screening_results_columns(engine)
    _ensure_job_runs_unique_key(engine)
    seed_default_presets()
