from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.crud.audio_crud import get_features, create_feature, delete_feature
from app.schemas.audio_schema import AudioFeatureCreate, AudioFeatureRead

router = APIRouter(
    prefix="/patients/{patient_id}/assessments/{assessment_id}/recordings/{recording_id}/features",
    tags=["features"],
)

@router.get("/", response_model=List[AudioFeatureRead])
async def list_features(
    patient_id: int,
    assessment_id: int,
    recording_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    List all extracted audio‐features for a given recording.
    """
    return await get_features(db, recording_id)


@router.post(
    "/",
    response_model=AudioFeatureRead,
    status_code=status.HTTP_201_CREATED
)
async def add_feature(
    patient_id: int,
    assessment_id: int,
    recording_id: int,
    feature_in: AudioFeatureCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a single feature (name + value) to the given recording.
    """
    try:
        return await create_feature(db, recording_id, feature_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create feature: {e}"
        )


@router.delete(
    "/{feature_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_feature(
    patient_id: int,
    assessment_id: int,
    recording_id: int,
    feature_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a feature by its ID.
    """
    await delete_feature(db, feature_id)
    return None
