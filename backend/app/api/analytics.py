from fastapi import APIRouter, HTTPException
router = APIRouter()
@router.get("/indicators/{instrument_id}")
def indicators(instrument_id: int):
    raise HTTPException(status_code=501, detail="Not implemented yet")