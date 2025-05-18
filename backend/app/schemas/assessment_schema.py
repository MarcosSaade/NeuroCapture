# backend/app/schemas/assessment_schema.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional

# ─── Subscore Schemas ─────────────────────────────────────────────────────────

class SubscoreBase(BaseModel):
    name: str = Field(..., max_length=100)
    score: float = Field(..., ge=0)
    max_score: Optional[float] = Field(None, ge=0)

class SubscoreCreate(SubscoreBase):
    pass

class SubscoreRead(SubscoreBase):
    subscore_id: int

    model_config = ConfigDict(from_attributes=True)

class SubscoreUpdate(BaseModel):
    name: Optional[str] = None
    score: Optional[float] = None
    max_score: Optional[float] = None


# ─── Assessment Schemas ────────────────────────────────────────────────────────

class AssessmentBase(BaseModel):
    assessment_type: str = Field(..., max_length=50)
    score: float = Field(..., ge=0)
    max_possible_score: Optional[float] = None
    assessment_date: datetime
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    subscores: Optional[List[SubscoreCreate]] = None

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(BaseModel):
    assessment_type: Optional[str] = None
    score: Optional[float] = None
    max_possible_score: Optional[float] = None
    assessment_date: Optional[datetime] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    subscores: Optional[List[SubscoreCreate]] = None

class AssessmentInDB(AssessmentBase):
    assessment_id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
    subscores: List[SubscoreRead] = []

    model_config = ConfigDict(from_attributes=True)
