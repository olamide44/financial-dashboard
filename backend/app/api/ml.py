from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.config import settings
from core.deps import get_db, get_current_user
from db import models
from services.forecasts import train_and_forecast_for_instrument, load_forecast

router = APIRouter()

@router.post("/forecast/instrument/{instrument_id}")
def forecast_instrument(
    instrument_id: int,
    horizon_days: int = Query(None, ge=1, le=30),
    lookback_days: int = Query(None, ge=60, le=3650),
    model: str = Query(None, pattern="^(ridge|lasso)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not settings.ml_enable:
        raise HTTPException(503, "ML is disabled")
    inst = db.get(models.Instrument, instrument_id)
    if not inst:
        raise HTTPException(404, "Instrument not found")

    try:
        run_id = train_and_forecast_for_instrument(
            db,
            instrument_id=instrument_id,
            horizon_days=horizon_days,
            lookback_days=lookback_days,
            model_type=model,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"forecast failed: {e}")

    return {"run_id": run_id, "instrument_id": instrument_id}

@router.get("/forecast/results/{run_id}")
def forecast_results(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        payload = load_forecast(db, run_id)
    except ValueError:
        raise HTTPException(404, "Run not found")
    return payload
