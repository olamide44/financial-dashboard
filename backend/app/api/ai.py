from fastapi import APIRouter, HTTPException
router = APIRouter()
@router.post("/insights/portfolio/{portfolio_id}")
def insights(portfolio_id: str):
    raise HTTPException(status_code=501, detail="Not implemented yet")