from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, date
from typing import List, Tuple, Optional

import numpy as np
from sqlalchemy.orm import Session

from core.config import settings
from db import models

log = logging.getLogger("forecasts")

# ---------- helpers ----------

def _business_days(start_d: date, n: int) -> List[datetime]:
    """Return next n business days (mon-fri) as UTC midnights."""
    out = []
    d = start_d
    while len(out) < n:
        d = d + timedelta(days=1)
        if d.weekday() < 5:  # 0=Mon .. 6=Sun
            out.append(datetime(d.year, d.month, d.day, tzinfo=timezone.utc))
    return out

def _rolling_mean(x: np.ndarray, win: int) -> np.ndarray:
    if win <= 1:
        return x.copy()
    # simple efficient rolling via cumulative sum
    cs = np.cumsum(np.insert(x, 0, 0.0))
    m = (cs[win:] - cs[:-win]) / float(win)
    # left-pad with NaN to align
    pad = np.full(win - 1, np.nan)
    return np.concatenate([pad, m])

def _build_features(y: np.ndarray) -> Tuple[np.ndarray, List[str]]:
    """
    Build a small tabular feature set from daily close series.
    Features: lags [1,2,3,5,10,20], rolling means [5,20].
    """
    feats = []
    names = []
    for lag in [1, 2, 3, 5, 10, 20]:
        feats.append(np.roll(y, lag))
        names.append(f"lag_{lag}")
    for win in [5, 20]:
        feats.append(_rolling_mean(y, win))
        names.append(f"sma_{win}")
    X = np.vstack(feats).T
    # mask rows with NaNs (from rolling) or from lag shifts at the head
    mask = ~np.isnan(X).any(axis=1)
    return X[mask], names, mask

@dataclass
class ForecastPoint:
    ts: datetime
    yhat: float
    lower: float
    upper: float

# ---------- core ----------

def train_and_forecast_for_instrument(
    db: Session,
    instrument_id: int,
    horizon_days: int | None = None,
    lookback_days: int | None = None,
    model_type: str | None = None,
) -> int:
    """
    Trains a tiny regressor on lag/rolling features and produces a recursive forecast
    for the next N business days. Persists MLRun + Forecast rows. Returns run_id.
    """
    horizon = int(horizon_days or settings.forecast_horizon_days)
    lookback = int(lookback_days or settings.forecast_lookback_days)
    model_type = (model_type or settings.forecast_model or "ridge").lower()

    inst = db.get(models.Instrument, instrument_id)
    if not inst:
        raise ValueError("Instrument not found")

    since = datetime.now(timezone.utc) - timedelta(days=lookback)
    rows = (
        db.query(models.Price)
          .filter(models.Price.instrument_id == instrument_id)
          .filter(models.Price.ts >= since)
          .order_by(models.Price.ts.asc())
          .all()
    )
    if len(rows) < 60:
        raise ValueError("Not enough history to train (need >= 60 days)")

    ts = np.array([r.ts for r in rows])
    y = np.array([float(r.close) for r in rows], dtype=float)

    # features
    X, names, mask = _build_features(y)
    y_target = y[mask]

    # train/test split (last 30 obs as test to estimate residual sigma)
    n = len(y_target)
    split = max(30, int(n * 0.15))
    train_end = n - split
    X_tr, X_te = X[:train_end], X[train_end:]
    y_tr, y_te = y_target[:train_end], y_target[train_end:]

    # model
    if model_type == "lasso":
        from sklearn.linear_model import Lasso
        model = Lasso(alpha=0.001, random_state=42, max_iter=10000)
    else:
        from sklearn.linear_model import Ridge
        model = Ridge(alpha=1.0, random_state=42)

    model.fit(X_tr, y_tr)
    y_pred_te = model.predict(X_te)
    resid = y_te - y_pred_te
    sigma = float(np.std(resid, ddof=1)) if len(resid) > 1 else float(np.std(resid))

    # recursive forecast: use last known y and repeatedly append predictions
    y_hist = y.copy()
    preds: List[float] = []
    for _ in range(horizon):
        X_last, _, _ = _build_features(y_hist)
        if len(X_last) == 0:
            raise ValueError("Feature generation failed during recursion")
        x_new = X_last[-1:].reshape(1, -1)
        y_new = float(model.predict(x_new)[0])
        preds.append(y_new)
        y_hist = np.append(y_hist, y_new)

    # dates to predict (business days after last known)
    last_day = rows[-1].ts.date()
    future_ts = _business_days(last_day, horizon)

    z = float(settings.forecast_band_z or 1.96)
    band = z * sigma
    fpoints = [ForecastPoint(ts=t, yhat=p, lower=p - band, upper=p + band) for t, p in zip(future_ts, preds)]

    # persist MLRun + Forecasts
    run = models.MLRun(
        instrument_id=instrument_id,
        model_type=model_type,
        horizon_days=horizon,
        lookback_days=lookback,
        status="done",
        metrics={
            "sigma": sigma,
            "z": z,
            "band": band,
            "test_mae": float(np.mean(np.abs(resid))) if len(resid) else None,
            "test_mape": float(np.mean(np.abs(resid / (y_te + 1e-9)))) if len(resid) else None,
        },
    )
    db.add(run)
    db.flush()

    inserted = 0
    for fp in fpoints:
        row = models.Forecast(
            run_id=run.id,
            instrument_id=instrument_id,
            ts=fp.ts,
            yhat=fp.yhat,
            yhat_lower=fp.lower,
            yhat_upper=fp.upper,
        )
        db.add(row)
        inserted += 1
    db.commit()
    log.info("forecast_done", extra={"instrument": inst.symbol, "run_id": run.id, "inserted": inserted})
    return run.id

def load_forecast(db: Session, run_id: int) -> dict:
    run = db.get(models.MLRun, run_id)
    if not run:
        raise ValueError("run not found")
    rows = (
        db.query(models.Forecast)
          .filter(models.Forecast.run_id == run_id)
          .order_by(models.Forecast.ts.asc())
          .all()
    )
    return {
        "run_id": run_id,
        "instrument_id": run.instrument_id,
        "model_type": run.model_type,
        "horizon_days": run.horizon_days,
        "lookback_days": run.lookback_days,
        "status": run.status,
        "metrics": run.metrics,
        "points": [
            {"ts": r.ts, "yhat": float(r.yhat), "yhat_lower": float(r.yhat_lower), "yhat_upper": float(r.yhat_upper)}
            for r in rows
        ],
    }
