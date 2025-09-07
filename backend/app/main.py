from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
import init_db
from api.router import api_router
from core.logging import setup_logging
from contextlib import asynccontextmanager
import uvicorn
import os
from jobs.scheduler import start_scheduler, shutdown_scheduler

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if settings.run_jobs:
        start_scheduler()
    yield
    if settings.run_jobs:
        shutdown_scheduler()

app = FastAPI(lifespan=lifespan, title="AI Finance Dashboard API", version="0.1.0")


app.add_middleware(
CORSMiddleware,
allow_origins=settings.cors_origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))