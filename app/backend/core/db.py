from pathlib import Path

from sqlalchemy import create_engine
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


def init_db() -> None:
    from app.backend.repositories.sqlite import models

    global engine
    engine = create_engine(_database_url(), future=True)
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
