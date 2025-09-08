from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import func
from sqlalchemy.orm import Session
from core.config import settings
from db.database import SessionLocal
from db.models import Instrument, Price, Holding
from services.news import fetch_news_for_symbol, upsert_news_and_score
from services.market_data import get_provider
from services.forecasts import train_and_forecast_for_instrument

from db import models
import logging


log = logging.getLogger("jobs")

def poll_news_for_tracked_instruments():
    """
    Fetch recent news for tracked instruments (those in holdings),
    score sentiment, and store. Runs every NEWS_POLL_INTERVAL_MIN if enabled.
    """
    if not settings.enable_news_jobs:
        return
    db = SessionLocal()
    try:
        tracked = (
            db.query(models.Instrument)
              .join(models.Holding, models.Holding.instrument_id == models.Instrument.id)
              .group_by(models.Instrument.id)
              .all()
        )
        total = 0
        for inst in tracked:
            try:
                arts = fetch_news_for_symbol(inst.symbol)
                ins = upsert_news_and_score(db, inst, arts)
                total += ins
                log.info("news_ingest", extra={"symbol": inst.symbol, "inserted": ins})
            except Exception:
                log.exception("news_ingest_failed", extra={"symbol": inst.symbol})
        if total:
            log.info("news_ingest_total", extra={"inserted": total})
    finally:
        db.close()


def _backfill_benchmark(db: Session):
    sym = (settings.default_benchmark or "").strip().upper()
    if not sym:
        return
    provider = get_provider()
    # upsert benchmark row
    bench = db.query(models.Benchmark).filter(models.Benchmark.symbol == sym).first()
    if not bench:
        bench = models.Benchmark(symbol=sym, name=sym, type="ETF")
        db.add(bench)
        db.flush()
    # find latest ts
    latest = (
        db.query(models.BenchmarkPrice.ts)
        .filter(models.BenchmarkPrice.benchmark_id == bench.id)
        .order_by(models.BenchmarkPrice.ts.desc())
        .first()
    )
    start = None
    if latest:
        start = latest[0].date()

    bars = provider.daily_prices(sym, start=start)
    inserted = 0
    for b in bars:
        exists = (
            db.query(models.BenchmarkPrice)
            .filter(models.BenchmarkPrice.benchmark_id == bench.id, models.BenchmarkPrice.ts == b["ts"])
            .first()
        )
        if exists:
            continue
        db.add(models.BenchmarkPrice(
            benchmark_id=bench.id,
            ts=b["ts"], open=b["open"], high=b["high"], low=b["low"], close=b["close"],
            volume=b.get("volume"), source=str(type(provider).__name__),
        ))
        inserted += 1
    if inserted:
        db.commit()

async def nightly_backfill_prices() -> None:
    """
    Backfill daily OHLCV data for all instruments with holdings.
    Runs at the time specified by `settings.backfill_at` (e.g. "02:30" for 2:30 AM).
    """
    db: Session = SessionLocal()
    provider = get_provider()
    try:
        # Identify instruments that have holdings (distinct instrument IDs)
        instrument_ids = [row[0] for row in db.query(Holding.instrument_id).distinct().all()]
        for inst_id in instrument_ids:
            instrument = db.query(Instrument).get(inst_id)
            if instrument is None:
                continue

            # Find the latest stored price timestamp for this instrument
            last_ts: datetime | None = db.query(func.max(Price.ts)).filter(Price.instrument_id == inst_id).scalar()
            if last_ts:
                # Start from the day after the latest stored price
                start_date = last_ts + timedelta(days=1)
            else:
                # Backfill up to the configured lookback (default 5 years)
                start_date = datetime.timezone.utc() - timedelta(days=settings.backfill_default_lookback_days)

            # Fetch new bars from the provider
            async for bar in provider.daily_prices(instrument.symbol, start=start_date):
                price = Price(
                    instrument_id=inst_id,
                    ts=bar.ts,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                    source=bar.source,
                )
                # Use merge() to avoid duplicate (instrument_id, ts) rows
                db.merge(price)

            db.commit()
    finally:
        db.close()

async def intraday_refresh_prices() -> None:
    """
    Refresh the most recent price for a limited set of actively watched instruments.
    Runs at intervals defined by `settings.intraday_interval_sec` when `settings.intraday_enable` is True.
    """
    db: Session = SessionLocal()
    provider = get_provider()
    try:
        # Pick up to ACTIVE_SYMBOLS_LIMIT instruments by most recently updated holding
        instrument_ids = [
            row[0]
            for row in (
                db.query(Holding.instrument_id)
                .order_by(Holding.last_updated.desc())
                .limit(settings.active_symbols_limit)
                .all()
            )
        ]
        for inst_id in instrument_ids:
            instrument = db.query(Instrument).get(inst_id)
            if instrument is None:
                continue

            # Fetch the latest bar; provider returns an iterable of Price-like objects
            async for bar in provider.daily_prices(instrument.symbol, start=None, end=None):
                # Upsert the latest price
                price = Price(
                    instrument_id=inst_id,
                    ts=bar.ts,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                    source=bar.source,
                )
                db.merge(price)
                db.commit()
                # Only one bar is needed for the latest refresh
                break
    finally:
        db.close()

def nightly_forecasts_for_tracked():
    if not settings.ml_enable:
        return
    db = SessionLocal()
    try:
        tracked = (
            db.query(models.Instrument)
              .join(models.Holding, models.Holding.instrument_id == models.Instrument.id)
              .group_by(models.Instrument.id)
              .all()
        )
        for inst in tracked:
            try:
                train_and_forecast_for_instrument(db, inst.id, None, None, None)
            except Exception:
                log.exception("nightly_forecast_failed", extra={"symbol": inst.symbol})
    finally:
        db.close()