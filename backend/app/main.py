from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import patients, demographics
from app.api.v1.endpoints.assessments import router as assessments_router
from app.api.v1.endpoints.subscores import router as subscores_router

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

app.include_router(patients.router, prefix="/api/v1")
app.include_router(demographics.router, prefix="/api/v1")
app.include_router(assessments_router, prefix="/api/v1")
app.include_router(subscores_router, prefix="/api/v1")