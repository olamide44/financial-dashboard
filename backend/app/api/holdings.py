from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from core.deps import get_db, get_current_user
from db import models

router = APIRouter()

@router.get("/portfolios/{portfolio_id}/holdings")
def get_holdings(portfolio_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    portfolio = db.get(models.Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    account = db.get(models.Account, portfolio.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    holdings = db.query(models.Holding).filter(models.Holding.portfolio_id == portfolio_id).all()
    return [{
        "id": str(h.id),
        "instrument_id": h.instrument_id,
        "qty": float(h.qty),
        "cost_basis": float(h.cost_basis),
        "last_updated": h.last_updated,
    } for h in holdings]

@router.post("/portfolios/{portfolio_id}/holdings:bulk_upsert")
def bulk_upsert_holdings(portfolio_id: UUID, items: list[dict], db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    portfolio = db.get(models.Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    account = db.get(models.Account, portfolio.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = inserted = 0
    failed: list[dict] = []

    for item in items:
        symbol = str(item.get("symbol", "")).strip().upper()
        if not symbol:
            failed.append({"item": item, "reason": "missing_symbol"})
            continue
        qty = float(item.get("qty", 0))
        cost_basis = float(item.get("cost_basis", 0))
        exchange = item.get("exchange")

        instrument = (
            db.query(models.Instrument)
            .filter(models.Instrument.symbol == symbol)
            .first()
        )
        if not instrument:
            instrument = models.Instrument(symbol=symbol, exchange=exchange)
            db.add(instrument)
            db.flush()

        holding = (
            db.query(models.Holding)
            .filter(models.Holding.portfolio_id == portfolio_id, models.Holding.instrument_id == instrument.id)
            .first()
        )
        if holding:
            holding.qty = qty
            holding.cost_basis = cost_basis
            updated += 1
        else:
            db.add(models.Holding(portfolio_id=portfolio_id, instrument_id=instrument.id, qty=qty, cost_basis=cost_basis))
            inserted += 1

    db.commit()
    return {"updated": updated, "inserted": inserted, "failed": failed}