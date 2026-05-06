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
