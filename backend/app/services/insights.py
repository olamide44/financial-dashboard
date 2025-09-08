from __future__ import annotations
import math
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from core.config import settings
from db import models
from services.analytics import (
    equity_curve_from_holdings, pct_returns, max_drawdown, annualized_stats,
    cagr, sharpe_sortino, benchmark_series
)
from uuid import UUID

log = logging.getLogger("insights")

@dataclass
class HoldingSnapshot:
    symbol: str
    instrument_id: int
    qty: float
    last_close: float
    value: float
    weight: float

def _to_f(x) -> float:
    if x is None:
        return 0.0
    if isinstance(x, Decimal):
        return float(x)
    return float(x)

def _latest_close(db: Session, instrument_id: int) -> Optional[float]:
    row = (
        db.query(models.Price.close)
          .filter(models.Price.instrument_id == instrument_id)
          .order_by(models.Price.ts.desc())
          .first()
    )
    return _to_f(row[0]) if row else None

def _weights_and_concentration(holdings: List[HoldingSnapshot]) -> Dict[str, float]:
    # Herfindahl-Hirschman Index (HHI) and top-N concentration
    w = [h.weight for h in holdings if h.weight > 0]
    hhi = sum((wi * 100) ** 2 for wi in w)  # HHI on percentage weights
    top3 = sum(sorted(w, reverse=True)[:3])
    top5 = sum(sorted(w, reverse=True)[:5])
    return {"hhi": hhi, "top3": top3, "top5": top5}

def build_portfolio_snapshot(
    db: Session,
    portfolio_id: UUID,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    benchmark_symbol: Optional[str] = None,
) -> Dict:
    portfolio = db.get(models.Portfolio, portfolio_id)
    if not portfolio:
        raise ValueError("portfolio not found")

    # 1) holdings → values/weights at latest close
    holdings_raw = (
        db.query(models.Holding)
          .filter(models.Holding.portfolio_id == portfolio_id)
          .all()
    )
    hs: List[HoldingSnapshot] = []
    gross = 0.0
    for h in holdings_raw:
        qty = _to_f(h.qty)
        if qty == 0:
            continue
        px = _latest_close(db, h.instrument_id)
        if px is None:
            continue
        val = qty * px
        hs.append(HoldingSnapshot(
        symbol=db.get(models.Instrument, h.instrument_id).symbol,
        instrument_id=h.instrument_id, qty=qty, last_close=px, value=val, weight=0.0
        ))
        gross += val
    for i in range(len(hs)):
        hs[i].weight = 0.0 if gross == 0 else hs[i].value / gross

    # 2) equity & returns
    curve = equity_curve_from_holdings(db, portfolio_id, start, end)
    rets = pct_returns(curve)
    stats = annualized_stats(rets)
    mdd = max_drawdown(curve)
    risk_free = float(getattr(settings, "risk_free_rate_annual", 0.03))
    sharpe, sortino = sharpe_sortino(rets, risk_free)
    cg = cagr(curve)

    # 3) benchmark series (optional)
    bench_sym = (benchmark_symbol or getattr(settings, "default_benchmark", None) or "").strip().upper()
    bench = []
    if bench_sym:
        bench = benchmark_series(db, bench_sym, start, end)

    # 4) concentration
    conc = _weights_and_concentration(hs)
    hs_sorted = sorted(hs, key=lambda x: x.weight, reverse=True)

    return {
        "portfolio": {"id": portfolio_id, "name": portfolio.name, "base_currency": portfolio.base_currency},
        "snapshot": {
            "gross_value": gross,
            "holdings": [
                {
                    "symbol": h.symbol, "instrument_id": h.instrument_id, "qty": h.qty,
                    "last_close": h.last_close, "value": h.value, "weight": h.weight
                } for h in hs_sorted
            ],
            "concentration": conc,  # hhi, top3, top5 (fractions for top3/5)
        },
        "performance": {
            "start": curve[0].ts.isoformat() if curve else None,
            "end": curve[-1].ts.isoformat() if curve else None,
            "cagr": cg,
            "ann_return": stats["mu"],
            "ann_vol": stats["sigma"],
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": mdd,
        },
        "benchmark": {
            "symbol": bench_sym or None,
            "have_data": bool(bench),
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

# ---------- LLM integration ----------

def _make_prompt(snapshot: Dict) -> str:
    """
    Keep the prompt small and grounded. No PII, only computed numbers.
    """
    p = snapshot["performance"]
    s = snapshot["snapshot"]
    top = s["holdings"][:5]
    disclaimer = getattr(settings, "ai_disclaimer", "This is not financial advice.")
    lines = []
    lines.append("You are a careful investment assistant. Respond with 5 concise bullet points. Do not give absolute guarantees.")
    lines.append("Ground your advice ONLY in the provided numbers. If data is missing, say so briefly.")
    lines.append("")
    lines.append("PORTFOLIO SNAPSHOT:")
    lines.append(f"- Total value: {s['gross_value']:.2f}")
    lines.append(f"- Top holdings: " + ", ".join(f"{h['symbol']} ({h['weight']*100:.1f}%)" for h in top))
    lines.append(f"- Concentration: Top3 {s['concentration']['top3']*100:.1f}%, Top5 {s['concentration']['top5']*100:.1f}%, HHI {s['concentration']['hhi']:.0f}")
    lines.append("")
    lines.append("RISK / RETURN:")
    lines.append(f"- CAGR: {p['cagr']:.2%}  |  Ann Return: {p['ann_return']:.2%}  |  Ann Vol: {p['ann_vol']:.2%}")
    lines.append(f"- Sharpe: {p['sharpe']:.2f}  |  Sortino: {p['sortino']:.2f}  |  Max Drawdown: {p['max_drawdown']:.2%}")
    lines.append("")
    if snapshot["benchmark"]["symbol"]:
        lines.append(f"Benchmark: {snapshot['benchmark']['symbol']} (data_available={snapshot['benchmark']['have_data']})")
    lines.append("")
    lines.append("STYLE: Short, direct, numeric where possible. End with the disclaimer below.")
    lines.append(f"DISCLAIMER: {disclaimer}")
    return "\n".join(lines)

def _openai_chat(messages: list[dict]) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY missing")
    # OpenAI python client v1.x
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=settings.ai_model,
        messages=messages,
        temperature=float(settings.ai_temperature),
        max_tokens=int(settings.ai_max_tokens),
    )
    return resp.choices[0].message.content.strip()

def generate_insight_text(snapshot: Dict) -> str:
    prompt = _make_prompt(snapshot)
    system = (
        "You generate compact portfolio insights. Use only provided data. "
        "No financial advice—include the disclaimer verbatim at the end."
    )
    try:
        text = _openai_chat([
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ])
        return text
    except Exception as e:
        log.warning("llm_fallback: %s", e)
        # Fallback heuristic if LLM not available
        s = snapshot["snapshot"]; p = snapshot["performance"]
        bullets = []
        if s["concentration"]["top3"] > 0.6:
            bullets.append(f"- High concentration: top 3 positions = {s['concentration']['top3']*100:.1f}% of portfolio.")
        else:
            bullets.append(f"- Diversification looks reasonable: top 3 = {s['concentration']['top3']*100:.1f}%")
        bullets.append(f"- Volatility (ann): {p['ann_vol']:.2%}; Max drawdown: {p['max_drawdown']:.2%}.")
        bullets.append(f"- Return profile: CAGR {p['cagr']:.2%}, Sharpe {p['sharpe']:.2f}, Sortino {p['sortino']:.2f}.")
        if not snapshot["benchmark"]["have_data"]:
            bullets.append("- Benchmark data not available yet. Add SPY benchmark to compare.")
        else:
            bullets.append("- Compare against benchmark in the dashboard for context.")
        bullets.append(f"- {getattr(settings, 'ai_disclaimer', 'This is not financial advice.')}")
        return "\n".join(bullets)
