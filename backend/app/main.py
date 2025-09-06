from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.database import init_db
from api.router import api_router
from core.logging import setup_logging
from contextlib import asynccontextmanager


setup_logging()


app = FastAPI(title="AI Finance Dashboard API", version="0.1.0")


app.add_middleware(
CORSMiddleware,
allow_origins=settings.cors_origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()


app.include_router(api_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}