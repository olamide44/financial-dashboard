from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from core.deps import get_db, get_current_user
from db import models

router = APIRouter()

@router.post("/portfolios/{portfolio_id}/transactions", status_code=201)
def create_transaction(portfolio_id: UUID, symbol: str, type: str, qty: float, price: float, executed_at: str, fees: float = 0.0, exchange: str | None = None, note: str | None = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    portfolio = db.get(models.Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    account = db.get(models.Account, portfolio.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    symbol = symbol.strip().upper()
    instrument = (
        db.query(models.Instrument)
        .filter(models.Instrument.symbol == symbol)
        .first()
    )
    if not instrument:
        instrument = models.Instrument(symbol=symbol, exchange=exchange)
        db.add(instrument)
        db.flush()

    tx = models.Transaction(
        portfolio_id=portfolio_id,
        instrument_id=instrument.id,
        type=type,
        qty=qty,
        price=price,
        fees=fees,
        executed_at=executed_at,
        note=note,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return {
        "id": str(tx.id),
        "instrument_id": tx.instrument_id,
        "type": tx.type,
        "qty": float(tx.qty),
        "price": float(tx.price),
        "fees": float(tx.fees),
        "executed_at": tx.executed_at,
        "note": tx.note,
    }