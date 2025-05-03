from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone

class PatientBase(BaseModel):
    study_identifier: str = Field(..., title="External Study ID", max_length=50)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    study_identifier: str | None = Field(None, title="External Study ID", max_length=50)

class PatientInDBBase(PatientBase):
    patient_id: int
    created_at: datetime
    updated_at: datetime

    # Pydantic v2: use model_config for ORM compatibility
    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    def force_utc(cls, v: datetime) -> datetime:
        # If SQLAlchemy/SQLite gave us a naive datetime, assume UTC
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class Patient(PatientInDBBase):
    pass

class PatientInDB(PatientInDBBase):
    pass
