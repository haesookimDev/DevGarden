from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, posts, portfolio, upload, ai_generation, settings as settings_router
from app.config import settings
from app.services.storage_service import StorageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MinIO buckets
    storage = StorageService()
    storage.ensure_buckets()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(ai_generation.router, prefix="/api/v1/generate", tags=["ai-generation"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["settings"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}
