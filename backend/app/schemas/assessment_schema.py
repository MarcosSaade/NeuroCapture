from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class SubscoreBase(BaseModel):
    name: str = Field(..., max_length=100)
    score: float = Field(..., ge=0)
    max_score: float | None = None

class SubscoreCreate(SubscoreBase):
    pass

class SubscoreRead(SubscoreBase):
    subscore_id: int

    model_config = ConfigDict(from_attributes=True)

class SubscoreUpdate(BaseModel):
    name: str | None = None
    score: float | None = None
    max_score: float | None = None


class AssessmentBase(BaseModel):
    assessment_type: str = Field(..., max_length=50)
    score: float = Field(..., ge=0)
    max_possible_score: float | None = None
    assessment_date: datetime
    diagnosis: str | None = None
    notes: str | None = None

class AssessmentCreate(AssessmentBase):
    # allow nested subscores
    subscores: List[SubscoreCreate] | None = None

class AssessmentUpdate(BaseModel):
    assessment_type: str | None = None
    score: float | None = None
    max_possible_score: float | None = None
    assessment_date: datetime | None = None
    diagnosis: str | None = None
    notes: str | None = None
    subscores: List[SubscoreCreate] | None = None

class AssessmentInDB(AssessmentBase):
    assessment_id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
    subscores: List[SubscoreRead] = []

    model_config = ConfigDict(from_attributes=True)
