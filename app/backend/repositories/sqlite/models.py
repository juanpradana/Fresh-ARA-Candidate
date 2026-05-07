from sqlalchemy import Column, Float, Integer, Text

from app.backend.core.db import Base


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(Text, unique=True, nullable=False)
    symbol = Column(Text, nullable=False)


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screen_date = Column(Text, nullable=False)
    ticker = Column(Text, nullable=False)
    preset_name = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    rank_num = Column(Integer, nullable=False)
    pass_count = Column(Integer, nullable=False)
    category = Column(Text, nullable=False)


class JobRun(Base):
    __tablename__ = "job_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_date = Column(Text, unique=True, nullable=False)
    status = Column(Text, nullable=False)
    error_message = Column(Text, nullable=True)
    started_at = Column(Text, nullable=False)
    finished_at = Column(Text, nullable=True)
