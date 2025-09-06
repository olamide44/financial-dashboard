from fastapi import APIRouter, HTTPException
router = APIRouter()
@router.post("/forecast/instrument/{instrument_id}")
def forecast(instrument_id: int):
    raise HTTPException(status_code=501, detail="Not implemented yet")