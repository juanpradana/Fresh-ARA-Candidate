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


def init_db() -> None:
    from app.backend.repositories.sqlite import models

    global engine
    engine = create_engine(_database_url(), future=True)
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    _ensure_job_runs_columns(engine)
