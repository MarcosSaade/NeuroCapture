# backend/app/schemas/audio_schema.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# ─── Audio Recording Schemas ─────────────────────────────────────────────────

class AudioRecordingBase(BaseModel):
    filename: str
    file_path: str
    recording_date: datetime
    recording_device: Optional[str] = None
    task_type: Optional[str] = None

class AudioRecordingCreate(AudioRecordingBase):
    pass

class AudioRecordingRead(AudioRecordingBase):
    recording_id: int
    assessment_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ─── Audio Feature Schemas ───────────────────────────────────────────────────

class AudioFeatureBase(BaseModel):
    feature_name: str = Field(..., max_length=50)
    feature_value: float

class AudioFeatureCreate(AudioFeatureBase):
    pass

class AudioFeatureRead(AudioFeatureBase):
    feature_id: int
    recording_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
