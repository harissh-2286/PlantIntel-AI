import os
import sys
import logging

# Ensure backend directory is first in sys.path for app module imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir in sys.path:
    sys.path.remove(backend_dir)
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.api import quality, predict, endpoints, explain, severity, history, guidance, plants
from app.database.database import init_db
from app.ml.model import ai_model

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Load Model
    init_db()
    ai_model.load_model()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="PlantIntel AI",
    description="AI Plant Disease Intelligence, Explainability & Continuous Monitoring Platform",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for both dev and production deployment
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "PlantIntel AI",
        "version": "2.0.0",
        "phase": 12,
        "mode": "production",
        "modules": ["disease_classification", "severity_estimation", "explainability", "plant_health_guidance", "continuous_monitoring"]
    }

# Include API Endpoints
app.include_router(quality.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(endpoints.router, prefix="/api")
app.include_router(explain.router, prefix="/api")
app.include_router(severity.router, prefix="/api")
app.include_router(history.router, prefix="/api")
# Phase 12 — Plant Health Guidance & Continuous Monitoring
app.include_router(guidance.router, prefix="/api")
app.include_router(plants.router, prefix="/api")

# Static Frontend Mounting for Unified Deployment
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(frontend_dist):
    logging.info(f"[DEPLOYMENT] Mounting static frontend build from: {frontend_dist}")
    
    # Mount assets subfolder if present
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Prevent intercepting API endpoints
        if full_path.startswith("api/"):
            return None
        
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to SPA index.html for client-side routing
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
