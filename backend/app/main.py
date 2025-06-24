"""
NeuroCapture FastAPI Application

Main application entry point for the NeuroCapture neurological assessment platform.
Provides RESTful API endpoints for patient management, cognitive assessments,
audio processing, and data export functionality.

Author: NeuroCapture Development Team
Version: 0.1.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import API routers
from app.api.v1.endpoints import patients, demographics
from app.api.v1.endpoints.assessments import router as assessments_router
from app.api.v1.endpoints.subscores import router as subscores_router
from app.api.v1.endpoints.recordings import router as recordings_router
from app.api.v1.endpoints.features import router as features_router
from app.api.v1.endpoints.audio_processing import router as audio_processing_router
from app.api.v1.endpoints.export import router as export_router

# Initialize FastAPI application
app = FastAPI(
    title="NeuroCapture API",
    description="RESTful API for neurological assessment and audio analysis",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc documentation
)

# Configure CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite development server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Serve static files (audio recordings and uploads)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register API routers with versioned prefix
API_V1_PREFIX = "/api/v1"

app.include_router(patients.router, prefix=API_V1_PREFIX, tags=["patients"])
app.include_router(demographics.router, prefix=API_V1_PREFIX, tags=["demographics"])
app.include_router(assessments_router, prefix=API_V1_PREFIX, tags=["assessments"])
app.include_router(subscores_router, prefix=API_V1_PREFIX, tags=["subscores"])
app.include_router(recordings_router, prefix=API_V1_PREFIX, tags=["recordings"])
app.include_router(features_router, prefix=API_V1_PREFIX, tags=["features"])
app.include_router(audio_processing_router, prefix=API_V1_PREFIX, tags=["audio-processing"])
app.include_router(export_router, prefix=API_V1_PREFIX, tags=["export"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "NeuroCapture API is running",
        "version": "0.1.0",
        "docs": "/docs"
    }
