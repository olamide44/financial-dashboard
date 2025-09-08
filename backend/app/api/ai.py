from __future__ import annotations
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.deps import get_db, get_current_user
from db import models
from services.insights import build_portfolio_snapshot, generate_insight_text

router = APIRouter()

@router.post("/insights/portfolio/{portfolio_id}")
def portfolio_insights(
    portfolio_id: str,
    benchmark: Optional[str] = Query(None, description="Override benchmark symbol, e.g. SPY"),
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    portfolio = db.get(models.Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(404, "Portfolio not found")
    account = db.get(models.Account, portfolio.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    start = datetime.fromisoformat(from_) if from_ else None
    end = datetime.fromisoformat(to) if to else None
    snap = build_portfolio_snapshot(db, portfolio_id, start, end, benchmark)
    text = generate_insight_text(snap)
    return {
        "portfolio_id": portfolio_id,
        "benchmark": snap["benchmark"]["symbol"],
        "generated_at": snap["generated_at"],
        "snapshot": snap,         # echo the numbers used (frontend can show details)
        "insight": text,          # the plain-English summary
    }
