from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from core.deps import get_db, get_current_user
from db import models

router = APIRouter()

@router.get("/me")
def list_my_portfolios(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    portfolios = (
        db.query(models.Portfolio)
        .join(models.Account)
        .filter(models.Account.user_id == current_user.id)
        .order_by(models.Portfolio.created_at.desc())
        .all()
    )
    return [{
        "id": str(p.id),
        "name": p.name,
        "base_currency": p.base_currency,
        "created_at": p.created_at,
    } for p in portfolios]

@router.post("/")
def create_portfolio(name: str, base_currency: str = "USD", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    account = (
        db.query(models.Account)
        .filter(models.Account.user_id == current_user.id)
        .order_by(models.Account.id)
        .first()
    )
    if not account:
        account = models.Account(user_id=current_user.id, display_name="Default")
        db.add(account)
        db.flush()
    p = models.Portfolio(account_id=account.id, name=name, base_currency=base_currency)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": str(p.id), "name": p.name, "base_currency": p.base_currency, "created_at": p.created_at}