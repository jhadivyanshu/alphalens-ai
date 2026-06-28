from sqlalchemy import Column, Integer, String, Numeric, BigInteger, Boolean, Text, TIMESTAMP, DATE, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    exchange = Column(String(10), default="NSE")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    prices = relationship("Price", back_populates="company")
    financials = relationship("Financial", back_populates="company")
    news = relationship("News", back_populates="company")
    documents = relationship("Document", back_populates="company")
    score = relationship("Score", back_populates="company", uselist=False)
    score_history = relationship("ScoreHistory", back_populates="company")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(DATE, nullable=False)
    open = Column(Numeric(12, 2))
    high = Column(Numeric(12, 2))
    low = Column(Numeric(12, 2))
    close = Column(Numeric(12, 2))
    volume = Column(BigInteger)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    company = relationship("Company", back_populates="prices")


class Financial(Base):
    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(20), nullable=False)
    period_type = Column(String(10), nullable=False)
    revenue = Column(Numeric(15, 2))
    pat = Column(Numeric(15, 2))
    ebitda = Column(Numeric(15, 2))
    ebitda_margin = Column(Numeric(6, 2))
    pat_margin = Column(Numeric(6, 2))
    eps = Column(Numeric(10, 2))
    roe = Column(Numeric(6, 2))
    roce = Column(Numeric(6, 2))
    debt = Column(Numeric(15, 2))
    cash = Column(Numeric(15, 2))
    operating_cf = Column(Numeric(15, 2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    company = relationship("Company", back_populates="financials")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(Text)
    source = Column(String(100))
    url = Column(Text)
    published_at = Column(TIMESTAMP)
    summary = Column(Text)
    sentiment = Column(String(10))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    company = relationship("Company", back_populates="news")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    doc_type = Column(String(20))
    year = Column(Integer)
    quarter = Column(String(10))
    file_path = Column(Text)
    raw_text = Column(Text)
    summary = Column(Text)
    sentiment = Column(String(10))
    management_promises = Column(JSONB)
    is_embedded = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    company = relationship("Company", back_populates="documents")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False)
    financial = Column(Numeric(5, 2))
    technical = Column(Numeric(5, 2))
    management = Column(Numeric(5, 2))
    sector = Column(Numeric(5, 2))
    risk = Column(Numeric(5, 2))
    overall = Column(Numeric(5, 2))
    reasons = Column(JSONB)
    warnings = Column(JSONB)
    calculated_at = Column(TIMESTAMP, default=datetime.utcnow)

    company = relationship("Company", back_populates="score")


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    financial = Column(Numeric(5, 2))
    technical = Column(Numeric(5, 2))
    management = Column(Numeric(5, 2))
    sector = Column(Numeric(5, 2))
    risk = Column(Numeric(5, 2))
    overall = Column(Numeric(5, 2))
    delta = Column(Numeric(5, 2))
    change_reasons = Column(JSONB)
    calculated_at = Column(TIMESTAMP, default=datetime.utcnow)

    company = relationship("Company", back_populates="score_history")