from fastapi import FastAPI
from app.api.v1.endpoints import patients

app = FastAPI(
    title="NeuroCapture API",
    version="0.1.0"
)

app.include_router(patients.router, prefix="/api/v1")
