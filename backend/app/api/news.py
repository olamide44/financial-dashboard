from fastapi import APIRouter, HTTPException
router = APIRouter()
@router.get("/{instrument_id}")
def news_for(instrument_id: int):
    raise HTTPException(status_code=501, detail="Not implemented yet")