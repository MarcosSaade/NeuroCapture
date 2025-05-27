from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import patients, demographics
from app.api.v1.endpoints.assessments import router as assessments_router
from app.api.v1.endpoints.subscores import router as subscores_router
from app.api.v1.endpoints.recordings import router as recordings_router
from app.api.v1.endpoints.features import router as features_router
from app.api.v1.endpoints.audio_processing import router as audio_processing_router
from app.api.v1.endpoints.export import router as export_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="NeuroCapture API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React/Vite dev URL
    allow_credentials=True,
    allow_methods=["*"],    # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # allow all headers
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(patients.router, prefix="/api/v1")
app.include_router(demographics.router, prefix="/api/v1")
app.include_router(assessments_router, prefix="/api/v1")
app.include_router(subscores_router, prefix="/api/v1")
app.include_router(recordings_router, prefix="/api/v1")
app.include_router(features_router, prefix="/api/v1")
app.include_router(audio_processing_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
