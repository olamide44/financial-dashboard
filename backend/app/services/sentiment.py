from __future__ import annotations
import logging, hashlib
from typing import Iterable, List, Dict, Tuple
from dataclasses import dataclass

from app.core.config import settings

log = logging.getLogger("sentiment")

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
except Exception as e:
    AutoTokenizer = AutoModelForSequenceClassification = pipeline = None
    log.warning("transformers import failed; sentiment disabled: %s", e)

@dataclass
class SentimentResult:
    label: str   # "positive" | "neutral" | "negative"
    score: float # probability in [0,1]

class FinbertSentiment:
    _nlp = None

    def _lazy_init(self):
        if self._nlp is not None:
            return
        if pipeline is None:
            raise RuntimeError("transformers not available; install dependencies")
        model_id = settings.sentiment_model
        self._nlp = pipeline(
            "text-classification",
            model=model_id,
            tokenizer=model_id,
            return_all_scores=False,
            truncation=True,
            max_length=512,
            device=-1,  # CPU
        )
        log.info("FinBERT pipeline loaded: %s", model_id)

    def score_texts(self, texts: List[str]) -> List[SentimentResult]:
        self._lazy_init()
        # Filter very short texts to avoid noise
        min_chars = max(0, settings.sentiment_min_chars)
        cleaned = [t if (t and len(t.strip()) >= min_chars) else "" for t in texts]
        preds = self._nlp(cleaned, batch_size=settings.sentiment_batch_size)
        out: List[SentimentResult] = []
        for p in preds:
            # FinBERT labels often are "positive"/"neutral"/"negative" already
            label = p["label"].lower()
            score = float(p.get("score", 0.0))
            out.append(SentimentResult(label=label, score=score))
        return out

sentiment_engine = FinbertSentiment()
