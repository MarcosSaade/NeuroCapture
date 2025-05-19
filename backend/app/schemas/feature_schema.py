from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class FeatureBase(BaseModel):
    feature_name: str = Field(..., max_length=50)
    feature_value: float

class FeatureCreate(FeatureBase):
    pass

class FeatureRead(FeatureBase):
    feature_id: int
    recording_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
