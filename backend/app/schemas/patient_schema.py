from pydantic import BaseModel, Field
from datetime import datetime

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

    class Config:
        orm_mode = True

class Patient(PatientInDBBase):
    pass

class PatientInDB(PatientInDBBase):
    # include any internal-only fields here if needed
    pass
