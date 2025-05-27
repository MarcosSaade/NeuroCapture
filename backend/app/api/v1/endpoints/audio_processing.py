# backend/app/api/v1/endpoints/audio_processing.py

import os
import asyncio
from typing import Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.crud.audio_crud import get_recording, create_feature
from app.schemas.audio_schema import AudioFeatureCreate
from app.services.task_manager import task_manager, TaskStatus
from app.services.audio_processing import clean_and_extract_features

# Import database dependencies here to avoid circular imports
from app.core.database import async_session


router = APIRouter(
    prefix="/patients/{patient_id}/assessments/{assessment_id}/recordings/{recording_id}",
    tags=["audio-processing"],
)

UPLOAD_DIR = os.getenv("AUDIO_UPLOAD_DIR", "uploads/recordings")

async def process_audio_background(task_id: str, recording_id: int, file_path: str):
    """Background task to process audio and extract features."""
    try:
        task_manager.mark_task_running(task_id)
        task_manager.update_task_progress(task_id, 0.1)
        
        # Get full file path - remove leading slash if present
        if file_path.startswith('/'):
            file_path = file_path[1:]
        full_file_path = file_path
        
        if not os.path.exists(full_file_path):
            raise FileNotFoundError(f"Audio file not found: {full_file_path}")
        
        task_manager.update_task_progress(task_id, 0.2)
        
        # Generate cleaned audio filename
        base, ext = os.path.splitext(full_file_path)
        cleaned_file_path = f"{base}_cleaned{ext}"
        
        task_manager.update_task_progress(task_id, 0.3)
        
        # Process audio and extract features
        features, cleaned_path = clean_and_extract_features(full_file_path, cleaned_file_path)
        
        task_manager.update_task_progress(task_id, 0.7)
        
        # Create new database session for background task
        async with async_session() as db:
            # Save features to database
            feature_count = 0
            total_features = len(features)
            
            for feature_name, feature_value in features.items():
                if isinstance(feature_value, (int, float)) and not (
                    isinstance(feature_value, float) and (
                        feature_value != feature_value or  # NaN check
                        feature_value == float('inf') or 
                        feature_value == float('-inf')
                    )
                ):
                    feature_create = AudioFeatureCreate(
                        feature_name=feature_name,
                        feature_value=float(feature_value)
                    )
                    await create_feature(db, recording_id, feature_create)
                    feature_count += 1
            
            # Commit the changes
            await db.commit()
        
        task_manager.update_task_progress(task_id, 0.9)
        
        # Store cleaned audio path in result
        result = {
            "features_extracted": feature_count,
            "cleaned_audio_path": "/" + cleaned_path if not cleaned_path.startswith('/') else cleaned_path,
            "original_features": total_features
        }
        
        task_manager.mark_task_completed(task_id, result)
        
    except Exception as e:
        task_manager.mark_task_failed(task_id, str(e))
        print(f"Error processing audio: {e}")
        import traceback
        traceback.print_exc()
        
        task_manager.update_task_progress(task_id, 0.7)
        
        # Create new database session for background task
        async with get_async_session() as db:
            # Save features to database
            feature_count = 0
            total_features = len(features)
            
            for feature_name, feature_value in features.items():
                if isinstance(feature_value, (int, float)) and not (
                    isinstance(feature_value, float) and (
                        feature_value != feature_value or  # NaN check
                        feature_value == float('inf') or 
                        feature_value == float('-inf')
                    )
                ):
                    feature_create = AudioFeatureCreate(
                        feature_name=feature_name,
                        feature_value=float(feature_value)
                    )
                    await create_feature(db, recording_id, feature_create)
                    feature_count += 1
        
        task_manager.update_task_progress(task_id, 0.9)
        
        # Store cleaned audio path in result
        result = {
            "features_extracted": feature_count,
            "cleaned_audio_path": os.path.join("/uploads/recordings", os.path.basename(cleaned_path)),
            "original_features": total_features
        }
        
        task_manager.mark_task_completed(task_id, result)
        
    except Exception as e:
        task_manager.mark_task_failed(task_id, str(e))
        print(f"Error processing audio: {e}")

@router.post("/process", status_code=status.HTTP_202_ACCEPTED)
async def start_audio_processing(
    patient_id: int,
    assessment_id: int,
    recording_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Start audio cleaning and feature extraction process in the background.
    Returns a task ID to track progress.
    """
    # Verify recording exists
    recording = await get_recording(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    # Create task
    task_id = task_manager.create_task()
    
    # Start background processing
    background_tasks.add_task(
        process_audio_background,
        task_id, 
        recording_id, 
        recording.file_path
    )
    
    return {
        "task_id": task_id,
        "message": "Audio processing started",
        "status": "accepted"
    }

@router.get("/process/{task_id}")
async def get_processing_status(
    patient_id: int,
    assessment_id: int,
    recording_id: int,
    task_id: str,
):
    """
    Get the status of an audio processing task.
    """
    task_info = task_manager.get_task_dict(task_id)
    
    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task_info
