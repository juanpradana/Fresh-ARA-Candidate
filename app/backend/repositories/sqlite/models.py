from sqlalchemy import Column, Integer, Text

from app.backend.core.db import Base


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(Text, unique=True, nullable=False)
    symbol = Column(Text, nullable=False)
