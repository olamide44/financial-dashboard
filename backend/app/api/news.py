from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db import models
from app.core.config import settings

router = APIRouter()

@router.get("/{instrument_id}")
def list_news(
    instrument_id: int,
    window_days: int = Query(7, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inst = db.get(models.Instrument, instrument_id)
    if not inst:
        raise HTTPException(404, "Instrument not found")
    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    q = (
        db.query(models.NewsArticle)
          .filter(models.NewsArticle.instrument_id == instrument_id)
          .filter(models.NewsArticle.published_at >= since)
          .order_by(models.NewsArticle.published_at.desc())
    )
    rows = q.all()
    return {
        "instrument_id": instrument_id,
        "count": len(rows),
        "articles": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "source": r.source_name,
                "url": r.url,
                "image_url": r.image_url,
                "published_at": r.published_at,
                "sentiment": {"label": r.sentiment_label, "score": float(r.sentiment_score) if r.sentiment_score is not None else None},
            } for r in rows
        ],
    }
