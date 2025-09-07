from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.deps import get_db, get_current_user
from db import models

router = APIRouter()

def _label_to_signed(label: str) -> int:
    if label == "positive":
        return 1
    if label == "negative":
        return -1
    return 0

@router.get("/{instrument_id}")
def sentiment_rolling(
    instrument_id: int,
    window_days: int = Query(7, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inst = db.get(models.Instrument, instrument_id)
    if not inst:
        raise HTTPException(404, "Instrument not found")

    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    rows = (
        db.query(
            func.date_trunc("day", models.NewsArticle.published_at).label("day"),
            func.count(models.NewsArticle.id),
            func.sum(
                func.case(
                    (
                        (models.NewsArticle.sentiment_label == "positive", 1),
                    ),
                    else_=0,
                )
            ).label("pos"),
            func.sum(
                func.case(
                    (
                        (models.NewsArticle.sentiment_label == "negative", 1),
                    ),
                    else_=0,
                )
            ).label("neg"),
            func.sum(
                func.case(
                    (
                        (models.NewsArticle.sentiment_label == "neutral", 1),
                    ),
                    else_=0,
                )
            ).label("neu"),
        )
        .filter(models.NewsArticle.instrument_id == instrument_id)
        .filter(models.NewsArticle.published_at >= since)
        .group_by(func.date_trunc("day", models.NewsArticle.published_at))
        .order_by(func.date_trunc("day", models.NewsArticle.published_at).asc())
        .all()
    )

    # build simple net score = (pos - neg) / total per day
    out = []
    for day, total, pos, neg, neu in rows:
        total = int(total or 0)
        pos = int(pos or 0)
        neg = int(neg or 0)
        neu = int(neu or 0)
        net = ((pos - neg) / total) if total > 0 else 0.0
        out.append({
            "day": day,
            "total": total,
            "pos": pos,
            "neg": neg,
            "neu": neu,
            "net_score": net,
        })

    return {
        "instrument_id": instrument_id,
        "window_days": window_days,
        "daily": out,
    }
