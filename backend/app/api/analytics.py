# app/api/analytics.py
from __future__ import annotations
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db import models
from app.services import indicators as ind
from app.services.analytics import (
    equity_curve_from_holdings, pct_returns, max_drawdown,
    annualized_stats, cagr, sharpe_sortino, benchmark_series
)
from app.core.config import settings

router = APIRouter()

def _parse_csv_ints(s: Optional[str]) -> List[int]:
    if not s:
        return []
    out = []
    for tok in s.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            out.append(int(tok))
        except ValueError:
            pass
    return out

@router.get("/indicators/{instrument_id}")
def get_indicators(
    instrument_id: int,
    sma: Optional[str] = Query(None, description="comma-separated windows, e.g. 20,50"),
    ema: Optional[str] = Query(None, description="comma-separated windows, e.g. 200"),
    rsi: Optional[int] = Query(None, description="period, e.g. 14"),
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inst = db.get(models.Instrument, instrument_id)
    if not inst:
        raise HTTPException(404, "Instrument not found")

    q = db.query(models.Price).filter(models.Price.instrument_id == instrument_id)
    if from_:
        q = q.filter(models.Price.ts >= datetime.fromisoformat(from_))
    if to:
        q = q.filter(models.Price.ts <= datetime.fromisoformat(to))
    rows = q.order_by(models.Price.ts.asc()).all()
    closes = [(r.ts, float(r.close)) for r in rows]

    resp = {"instrument_id": instrument_id, "count": len(closes), "indicators": {}}

    for w in _parse_csv_ints(sma):
        resp["indicators"][f"sma_{w}"] = [{"ts": ts, "v": val} for ts, val in ind.sma(closes, w)]
    for w in _parse_csv_ints(ema):
        resp["indicators"][f"ema_{w}"] = [{"ts": ts, "v": val} for ts, val in ind.ema(closes, w)]
    if rsi and rsi > 0:
        resp["indicators"][f"rsi_{rsi}"] = [{"ts": ts, "v": val} for ts, val in ind.rsi(closes, rsi)]
    return resp

@router.get("/portfolios/{portfolio_id}/performance")
def portfolio_performance(
    portfolio_id: str,
    benchmark: Optional[str] = Query(None, description="e.g. SPY"),
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

    curve = equity_curve_from_holdings(db, portfolio_id, start, end)
    rets = pct_returns(curve)
    stats = annualized_stats(rets)
    mdd = max_drawdown(curve)
    risk_free = settings.risk_free_rate_annual
    sharpe, sortino = sharpe_sortino(rets, risk_free)
    cg = cagr(curve)

    payload = {
        "portfolio_id": portfolio_id,
        "series": [{"ts": p.ts, "value": p.value} for p in curve],
        "returns": [{"ts": ts, "ret": r} for ts, r in rets],
        "metrics": {
            "start": curve[0].ts if curve else None,
            "end": curve[-1].ts if curve else None,
            "days": (curve[-1].ts - curve[0].ts).days if len(curve) >= 2 else 0,
            "cagr": cg,
            "ann_return": stats["mu"],
            "ann_vol": stats["sigma"],
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": mdd,
            "risk_free_rate_annual": risk_free,
        },
    }

    sym = (benchmark or settings.default_benchmark or "").strip().upper()
    if sym:
        b_series = benchmark_series(db, sym, start, end)
        payload["benchmark"] = {"symbol": sym, "series": [{"ts": p.ts, "value": p.value} for p in b_series]}
    return payload

@router.get("/portfolios/{portfolio_id}/stats")
def portfolio_stats(
    portfolio_id: str,
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
    curve = equity_curve_from_holdings(db, portfolio_id, start, end)
    rets = pct_returns(curve)
    stats = annualized_stats(rets)
    mdd = max_drawdown(curve)
    risk_free = settings.risk_free_rate_annual
    sharpe, sortino = sharpe_sortino(rets, risk_free)
    return {
        "portfolio_id": portfolio_id,
        "metrics": {
            "start": curve[0].ts if curve else None,
            "end": curve[-1].ts if curve else None,
            "days": (curve[-1].ts - curve[0].ts).days if len(curve) >= 2 else 0,
            "cagr": cagr(curve),
            "ann_return": stats["mu"],
            "ann_vol": stats["sigma"],
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": mdd,
            "risk_free_rate_annual": risk_free,
        },
    }
