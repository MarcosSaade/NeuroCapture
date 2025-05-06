from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class AssessmentBase(BaseModel):
    assessment_type: str = Field(..., max_length=50)
    score: float = Field(..., ge=0)
    max_possible_score: float | None = None
    assessment_date: datetime
    diagnosis: str | None = None
    notes: str | None = None

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(BaseModel):
    assessment_type: str | None = None
    score: float | None = None
    max_possible_score: float | None = None
    assessment_date: datetime | None = None
    diagnosis: str | None = None
    notes: str | None = None

class AssessmentInDB(AssessmentBase):
    assessment_id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
