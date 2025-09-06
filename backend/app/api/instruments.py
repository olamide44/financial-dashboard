from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.deps import get_db
from db import models
from services.market_data import get_provider

router = APIRouter()

@router.get("/search")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    # First, try local matches
    local = (
        db.query(models.Instrument)
        .filter(models.Instrument.symbol.ilike(f"%{q}%"))
        .limit(10).all()
    )
    results = [{
        "id": inst.id,
        "symbol": inst.symbol,
        "exchange": inst.exchange,
        "asset_class": inst.asset_class,
        "currency": inst.currency,
        "sector": inst.sector,
        "industry": inst.industry,
    } for inst in local]

    # Augment via provider search and upsert in DB
    try:
        provider = get_provider()
        ext = provider.search(q, limit=5)
        for it in ext:
            symbol = (it.get("symbol") or "").upper()
            if not symbol:
                continue
            existing = (
                db.query(models.Instrument)
                .filter(models.Instrument.symbol == symbol)
                .first()
            )
            if not existing:
                newi = models.Instrument(
                    symbol=symbol,
                    exchange=it.get("exchange"),
                    asset_class=it.get("asset_class"),
                    currency=it.get("currency"),
                    sector=it.get("sector"),
                    industry=it.get("industry"),
                )
                db.add(newi)
                db.flush()
                results.append({
                    "id": newi.id,
                    "symbol": newi.symbol,
                    "exchange": newi.exchange,
                    "asset_class": newi.asset_class,
                    "currency": newi.currency,
                    "sector": newi.sector,
                    "industry": newi.industry,
                })
    finally:
        db.commit()

    # Deduplicate by symbol keeping first
    seen = set()
    dedup = []
    for r in results:
        if r["symbol"] in seen:
            continue
        seen.add(r["symbol"])
        dedup.append(r)
    return dedup

@router.get("/{instrument_id}")
def get_instrument(instrument_id: int, db: Session = Depends(get_db)):
    inst = db.get(models.Instrument, instrument_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return {
        "id": inst.id,
        "symbol": inst.symbol,
        "exchange": inst.exchange,
        "asset_class": inst.asset_class,
        "currency": inst.currency,
        "sector": inst.sector,
        "industry": inst.industry,
    }