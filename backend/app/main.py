from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
import init_db
from api.router import api_router
from core.logging import setup_logging
from contextlib import asynccontextmanager
import uvicorn
import os

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
    yield


app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))