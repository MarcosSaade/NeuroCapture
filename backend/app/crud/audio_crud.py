# backend/app/crud/audio_crud.py

from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models import AudioRecording as AudioModel, AudioFeature as FeatureModel
from app.schemas.audio_schema import (
    AudioRecordingCreate,
    AudioRecordingRead,
    AudioFeatureCreate,
    AudioFeatureRead,
)

# ─── Recordings CRUD ─────────────────────────────────────────────────────────

async def get_recordings_for_assessment(
    db: AsyncSession, assessment_id: int
) -> List[AudioModel]:
    result = await db.execute(
        select(AudioModel).where(AudioModel.assessment_id == assessment_id)
    )
    return result.scalars().all()

async def get_recording(db: AsyncSession, recording_id: int) -> AudioModel | None:
    return await db.get(AudioModel, recording_id)

async def create_audio_recording(
    db: AsyncSession,
    assessment_id: int,
    obj_in: AudioRecordingCreate,
) -> AudioModel:
    db_obj = AudioModel(assessment_id=assessment_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_recording(db: AsyncSession, recording_id: int) -> None:
    obj = await get_recording(db, recording_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Delete physical audio files before deleting the database record
    import os
    try:
        file_path = obj.file_path
        if file_path.startswith('/uploads/recordings/'):
            # Remove the leading slash to get relative path
            relative_path = file_path[1:]
            if os.path.exists(relative_path):
                os.remove(relative_path)
                print(f"Deleted audio file: {relative_path}")
                
            # Also try to delete cleaned version if it exists
            base, ext = os.path.splitext(relative_path)
            cleaned_path = f"{base}_cleaned{ext}"
            if os.path.exists(cleaned_path):
                os.remove(cleaned_path)
                print(f"Deleted cleaned audio file: {cleaned_path}")
                
    except Exception as file_error:
        print(f"Warning: Could not delete audio file {obj.file_path}: {file_error}")
    
    # Delete the database record (CASCADE will handle features)
    await db.delete(obj)
    await db.commit()

# ─── Features CRUD ────────────────────────────────────────────────────────────

async def get_features(
    db: AsyncSession, recording_id: int
) -> List[FeatureModel]:
    result = await db.execute(
        select(FeatureModel).where(FeatureModel.recording_id == recording_id)
    )
    return result.scalars().all()

async def create_feature(
    db: AsyncSession, recording_id: int, obj_in: AudioFeatureCreate
) -> FeatureModel:
    db_obj = FeatureModel(recording_id=recording_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_feature(db: AsyncSession, feature_id: int) -> None:
    obj = await db.get(FeatureModel, feature_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Feature not found")
    await db.delete(obj)
    await db.commit()
