from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import router as api_router
from app.services.generator import MusicGeneratorService

@asynccontextmanager
async def lifespan(app: FastAPI):
    MusicGeneratorService.initialize()
    yield

app = FastAPI(title="AI Grunge Jam Generator", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(api_router, prefix="/api")
app.mount("/", StaticFiles(directory="static", html=True), name="static")
