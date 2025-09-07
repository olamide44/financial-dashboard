from __future__ import annotations
import httpx, logging, hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import models
from app.services.sentiment import sentiment_engine

log = logging.getLogger("news")

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

def _sha256(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

def _parse_dt(s: str | None) -> Optional[datetime]:
    if not s:
        return None
    # normalize Z to +00:00 for fromisoformat
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def _news_query_for_symbol(symbol: str) -> str:
    # simple query; you can enrich later with company name if available
    return f"{symbol}"

def fetch_news_for_symbol(symbol: str) -> List[Dict[str, Any]]:
    """
    Returns raw NewsAPI article dicts for a single symbol, sorted newest-first.
    """
    if not settings.newsapi_key:
        log.warning("NEWSAPI_KEY missing; skipping fetch for %s", symbol)
        return []
    params = {
        "q": _news_query_for_symbol(symbol),
        "language": settings.news_lang or "en",
        "sortBy": "publishedAt",
        "pageSize": settings.news_max_per_symbol,
        # from= ISO8601 date
        "from": (datetime.now(timezone.utc) - timedelta(days=settings.news_window_days)).date().isoformat(),
    }
    sources = (settings.news_sources or "").strip()
    if sources:
        params["sources"] = sources

    headers = {"X-Api-Key": settings.newsapi_key}
    with httpx.Client(timeout=20) as client:
        r = client.get(NEWS_ENDPOINT, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "ok":
            log.warning("NewsAPI status not ok: %s", data)
            return []
        return data.get("articles", []) or []

def upsert_news_and_score(db: Session, instrument: models.Instrument, articles: List[Dict[str, Any]]) -> int:
    """
    Dedupe by URL hash; insert new articles and score sentiment.
    Returns number of inserted rows.
    """
    if not articles:
        return 0

    texts: List[str] = []
    payloads: List[Dict[str, Any]] = []
    for a in articles:
        url = a.get("url") or ""
        url_hash = _sha256(url)
        published_at = _parse_dt(a.get("publishedAt"))
        if not published_at:
            continue
        title = (a.get("title") or "").strip()
        desc = (a.get("description") or "").strip()
        text = (title + ". " + desc).strip()
        texts.append(text)
        payloads.append({
            "instrument_id": instrument.id,
            "symbol": instrument.symbol,
            "title": title[:512],
            "description": desc[:4000] if desc else None,
            "source_name": (a.get("source") or {}).get("name"),
            "url": url[:1024],
            "url_hash": url_hash,
            "image_url": (a.get("urlToImage") or "")[:1024] or None,
            "published_at": published_at,
        })

    # sentiment in batch
    try:
        scores = sentiment_engine.score_texts(texts)
    except Exception as e:
        log.exception("sentiment_failed")
        # fallback to neutral
        scores = [{"label": "neutral", "score": 0.0} for _ in texts]

    inserted = 0
    for p, s in zip(payloads, scores):
        exists = (
            db.query(models.NewsArticle)
              .filter(models.NewsArticle.url_hash == p["url_hash"])
              .first()
        )
        if exists:
            continue
        row = models.NewsArticle(
            **p,
            sentiment_label=s.label,
            sentiment_score=s.score,
        )
        db.add(row)
        inserted += 1
    if inserted:
        db.commit()
    return inserted
