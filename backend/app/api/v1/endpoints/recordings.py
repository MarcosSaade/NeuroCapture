# backend/app/api/v1/endpoints/recordings.py

from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.crud.audio_crud import create_audio_recording, get_recordings_for_assessment
from app.schemas.audio_schema import AudioRecordingCreate
from app.schemas.audio_schema import AudioRecordingRead

router = APIRouter(
    prefix="/patients/{patient_id}/assessments/{assessment_id}/recordings",
    tags=["recordings"],
)

@router.post(
    "/",
    response_model=AudioRecordingRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_recording(
    *,
    patient_id: int,
    assessment_id: int,
    file: UploadFile = File(...),
    recording_date: datetime = Form(...),
    recording_device: str = Form(...),
    task_type: str = Form(None),
    db: AsyncSession = Depends(get_db),
) -> AudioRecordingRead:
    meta = AudioRecordingCreate(
        filename=file.filename,
        recording_date=recording_date,
        recording_device=recording_device,
        task_type=task_type,
    )
    return await create_audio_recording(db, assessment_id, file, meta)

@router.get(
    "/",
    response_model=list[AudioRecordingRead],
)
async def list_recordings(
    *,
    patient_id: int,
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[AudioRecordingRead]:
    return await get_recordings_for_assessment(db, assessment_id)
