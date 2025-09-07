# app/services/analytics.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from math import sqrt
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from db import models
from core.config import settings

@dataclass
class SeriesPoint:
    ts: datetime
    value: float

def _to_float(x) -> float:
    # SQLAlchemy Numeric -> float
    return float(x) if x is not None else 0.0

def equity_curve_from_holdings(db: Session, portfolio_id, start: Optional[datetime], end: Optional[datetime]) -> List[SeriesPoint]:
    """
    Build portfolio equity curve by summing qty * close across holdings per date.
    """
    # Get holdings snapshot (assumes current qty; extend later with transaction-aware PnL if needed)
    holdings = (
        db.query(models.Holding)
        .filter(models.Holding.portfolio_id == portfolio_id)
        .all()
    )
    if not holdings:
        return []

    # For each instrument, load prices in range and accumulate
    by_date: Dict[datetime, float] = {}
    for h in holdings:
        qty = _to_float(h.qty)
        if qty == 0:
            continue
        q = db.query(models.Price).filter(models.Price.instrument_id == h.instrument_id)
        if start:
            q = q.filter(models.Price.ts >= start)
        if end:
            q = q.filter(models.Price.ts <= end)
        q = q.order_by(models.Price.ts.asc())
        for row in q.all():
            ts = row.ts
            val = qty * _to_float(row.close)
            by_date[ts] = by_date.get(ts, 0.0) + val

    # sort into series
    series = [SeriesPoint(ts=k, value=v) for k, v in by_date.items()]
    series.sort(key=lambda p: p.ts)
    return series

def pct_returns(series: List[SeriesPoint]) -> List[Tuple[datetime, float]]:
    out: List[Tuple[datetime, float]] = []
    prev: Optional[float] = None
    for p in series:
        if prev is None:
            out.append((p.ts, 0.0))
        else:
            r = 0.0 if prev == 0 else (p.value / prev - 1.0)
            out.append((p.ts, r))
        prev = p.value
    return out

def max_drawdown(series: List[SeriesPoint]) -> float:
    peak = None
    max_dd = 0.0
    for p in series:
        v = p.value
        if peak is None or v > peak:
            peak = v
        if peak and v < peak:
            dd = v / peak - 1.0
            if dd < max_dd:
                max_dd = dd
    return max_dd  # negative number

def annualized_stats(returns: List[Tuple[datetime, float]]) -> Dict[str, float]:
    if not returns:
        return {"mu": 0.0, "sigma": 0.0}
    r = [x[1] for x in returns[1:]]  # skip first 0.0
    if not r:
        return {"mu": 0.0, "sigma": 0.0}
    n = len(r)
    mu = sum(r) / n
    # sample stddev
    var = sum((x - mu)**2 for x in r) / (n - 1) if n > 1 else 0.0
    sigma = sqrt(var)
    ann_mu = mu * 252.0
    ann_sigma = sigma * sqrt(252.0)
    return {"mu": ann_mu, "sigma": ann_sigma}

def cagr(series: List[SeriesPoint]) -> float:
    if len(series) < 2:
        return 0.0
    start = series[0].value
    end = series[-1].value
    if start <= 0:
        return 0.0
    days = (series[-1].ts - series[0].ts).days or 1
    years = days / 365.25
    return (end / start) ** (1.0 / years) - 1.0

def sharpe_sortino(returns: List[Tuple[datetime, float]], rf_annual: float) -> Tuple[float, float]:
    if not returns or len(returns) < 2:
        return (0.0, 0.0)
    r = [x[1] for x in returns[1:]]
    n = len(r)
    rf_daily = rf_annual / 252.0
    mu = sum(r) / n
    # std dev
    var = sum((x - mu)**2 for x in r) / (n - 1) if n > 1 else 0.0
    sigma = sqrt(var)
    # downside deviation
    downs = [min(0.0, x) for x in (ri - rf_daily for ri in r)]
    if n > 1:
        dd_var = sum((x - 0.0) ** 2 for x in downs) / (n - 1)
    else:
        dd_var = 0.0
    dd_sigma = sqrt(dd_var)
    sharpe = 0.0 if sigma == 0 else ((mu - rf_daily) / sigma) * sqrt(252.0)
    sortino = 0.0 if dd_sigma == 0 else ((mu - rf_daily) / dd_sigma) * sqrt(252.0)
    return (sharpe, sortino)

def ensure_benchmark(db: Session, symbol: str) -> models.Benchmark:
    # upsert benchmark by symbol
    b = db.query(models.Benchmark).filter(models.Benchmark.symbol == symbol.upper()).first()
    if b:
        return b
    b = models.Benchmark(symbol=symbol.upper(), name=symbol.upper(), type="ETF")
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

def benchmark_series(db: Session, symbol: str, start: Optional[datetime], end: Optional[datetime]) -> List[SeriesPoint]:
    b = ensure_benchmark(db, symbol)
    q = db.query(models.BenchmarkPrice).filter(models.BenchmarkPrice.benchmark_id == b.id)
    if start:
        q = q.filter(models.BenchmarkPrice.ts >= start)
    if end:
        q = q.filter(models.BenchmarkPrice.ts <= end)
    q = q.order_by(models.BenchmarkPrice.ts.asc())
    rows = q.all()
    return [SeriesPoint(ts=r.ts, value=float(r.close)) for r in rows]
