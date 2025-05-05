from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime, timezone

class DemographicBase(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., max_length=10)
    education_years: int | None = Field(None, ge=0, le=30)
    collection_date: date

class DemographicCreate(DemographicBase):
    pass

class DemographicUpdate(BaseModel):
    age: int | None = Field(None, ge=0, le=120)
    gender: str | None = Field(None, max_length=10)
    education_years: int | None = Field(None, ge=0, le=30)
    collection_date: date | None = None

class DemographicInDBBase(DemographicBase):
    demographic_id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def _force_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("created_at", "updated_at", mode="before")
    def _set_tz(cls, v):
        return cls._force_utc(v)

class Demographic(DemographicInDBBase):
    pass
