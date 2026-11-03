import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.core.config import settings
from backend.app.db.init_db import init_db
from backend.app.api.v1.endpoints import auth, vault, activity, dashboard, settings as settings_endpoint

app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-first digital trust and financial verification platform. Prove, Don't Share.",
    version="1.0.0-stage1"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include API v1 routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(vault.router, prefix=settings.API_V1_STR)
app.include_router(activity.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(settings_endpoint.router, prefix=settings.API_V1_STR)

# Static files for the web demo application
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "app": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "status": "RUNNING",
        "stage": "Stage 1: Application Foundation",
        "api_docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0-stage1"
    }

