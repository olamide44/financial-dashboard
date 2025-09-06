from fastapi import APIRouter
from api import auth, portfolios, holdings, transactions, instruments, prices, analytics, news, sentiment, ml, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(holdings.router, tags=["holdings"])
api_router.include_router(transactions.router, tags=["transactions"])

# Stubs for future routers so imports don’t fail
api_router.include_router(instruments.router, prefix="/instruments", tags=["instruments"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])