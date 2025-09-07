from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text, BigInteger, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from db.database import Base

utcnow = lambda: datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    pass_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    broker: Mapped[str | None] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(100), default="Default")
    user: Mapped["User"] = relationship(back_populates="accounts")
    portfolios: Mapped[list["Portfolio"]] = relationship(back_populates="account", cascade="all, delete-orphan")

class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    account: Mapped["Account"] = relationship(back_populates="portfolios")
    holdings: Mapped[list["Holding"]] = relationship(back_populates="portfolio", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="portfolio", cascade="all, delete-orphan")

class Instrument(Base):
    __tablename__ = "instruments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange: Mapped[str | None] = mapped_column(String(32))
    asset_class: Mapped[str | None] = mapped_column(String(32))
    currency: Mapped[str | None] = mapped_column(String(3))
    sector: Mapped[str | None] = mapped_column(String(64))
    industry: Mapped[str | None] = mapped_column(String(64))
    __table_args__ = (UniqueConstraint("symbol", "exchange", name="uq_symbol_exchange"),)

class Holding(Base):
    __tablename__ = "holdings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id", ondelete="RESTRICT"), index=True)
    qty: Mapped[float] = mapped_column(Numeric(18,6), default=0)
    cost_basis: Mapped[float] = mapped_column(Numeric(18,6), default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    portfolio: Mapped["Portfolio"] = relationship(back_populates="holdings")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id", ondelete="RESTRICT"), index=True)
    type: Mapped[str] = mapped_column(String(16))  # BUY/SELL/DIVIDEND/SPLIT
    qty: Mapped[float] = mapped_column(Numeric(18,6))
    price: Mapped[float] = mapped_column(Numeric(18,6))
    fees: Mapped[float] = mapped_column(Numeric(18,6), default=0)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    note: Mapped[str | None] = mapped_column(Text)
    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions")

class Price(Base):
    __tablename__ = "prices"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id", ondelete="CASCADE"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[float] = mapped_column(Numeric(18,6))
    high: Mapped[float] = mapped_column(Numeric(18,6))
    low: Mapped[float] = mapped_column(Numeric(18,6))
    close: Mapped[float] = mapped_column(Numeric(18,6))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(32))


    __table_args__ = (
    UniqueConstraint("instrument_id", "ts", name="uq_price_instrument_ts"),
    Index("ix_prices_inst_ts_desc", "instrument_id", "ts"),
    )
    
class Benchmark(Base):
    __tablename__ = "benchmarks"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(128))
    type: Mapped[str | None] = mapped_column(String(32))  # ETF, Index, etc.

class BenchmarkPrice(Base):
    __tablename__ = "benchmark_prices"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    benchmark_id: Mapped[int] = mapped_column(ForeignKey("benchmarks.id", ondelete="CASCADE"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[float] = mapped_column(Numeric(18,6))
    high: Mapped[float] = mapped_column(Numeric(18,6))
    low: Mapped[float] = mapped_column(Numeric(18,6))
    close: Mapped[float] = mapped_column(Numeric(18,6))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        UniqueConstraint("benchmark_id", "ts", name="uq_bench_price_ts"),
        Index("ix_bench_ts", "benchmark_id", "ts"),
    )
