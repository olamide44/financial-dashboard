from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.deps import get_db
from db import models
from services.market_data import get_provider
import logging

router = APIRouter()
logger = logging.getLogger("api.prices")

class SyncRequest(BaseModel):
    symbols: list[str]
    backfill_days: int | None = 1825  # ~5y

@router.post("/sync")
def sync_prices(payload: SyncRequest, db: Session = Depends(get_db)):
    provider = get_provider()
    inserted = 0
    errors: list[dict] = []

    start = None
    if payload.backfill_days and payload.backfill_days > 0:
        start = (datetime.now(timezone.utc) - timedelta(days=payload.backfill_days)).date()

    for sym in payload.symbols:
        symbol = sym.strip().upper()
        if not symbol:
            continue

        # ensure instrument exists
        inst = (
            db.query(models.Instrument)
            .filter(models.Instrument.symbol == symbol)
            .first()
        )
        if not inst:
            inst = models.Instrument(symbol=symbol)
            db.add(inst)
            db.flush()

        # fetch bars with error guard
        try:
            bars = provider.daily_prices(symbol, start=start)
        except Exception as e:
            logger.warning("provider_daily_failed", exc_info=True, extra={"symbol": symbol})
            errors.append({"symbol": symbol, "error": str(e)})
            bars = []

        # upsert new bars
        for b in bars:
            exists = (
                db.query(models.Price)
                .filter(models.Price.instrument_id == inst.id, models.Price.ts == b["ts"])
                .first()
            )
            if exists:
                continue
            p = models.Price(
                instrument_id=inst.id,
                ts=b["ts"],
                open=b["open"], high=b["high"], low=b["low"], close=b["close"],
                volume=b.get("volume"),
                source="alpha_vantage",
            )
            db.add(p)
            inserted += 1

    db.commit()
    return {"inserted": inserted, "errors": errors}

@router.get("/{instrument_id}")
def get_prices(instrument_id: int, interval: str = "1d", from_: str | None = None, to: str | None = None, db: Session = Depends(get_db)):
    if interval != "1d":
        raise HTTPException(status_code=400, detail="Only 1d supported for now")
    q = db.query(models.Price).filter(models.Price.instrument_id == instrument_id)
    if from_:
        try:
            dt_from = datetime.fromisoformat(from_)
            q = q.filter(models.Price.ts >= dt_from)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'from' date")
    if to:
        try:
            dt_to = datetime.fromisoformat(to)
            q = q.filter(models.Price.ts <= dt_to)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'to' date")
    q = q.order_by(models.Price.ts.asc())
    rows = q.all()
    return {
        "instrument_id": instrument_id,
        "interval": interval,
        "candles": [
            {"ts": r.ts, "o": float(r.open), "h": float(r.high), "l": float(r.low), "c": float(r.close), "v": r.volume}
            for r in rows
        ],
        "count": len(rows),
    }