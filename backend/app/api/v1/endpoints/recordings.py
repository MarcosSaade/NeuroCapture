import os, shutil
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.crud.audio_crud import (
    create_audio_recording,
    get_recordings_for_assessment,
    delete_recording,
)
from app.schemas.audio_schema import AudioRecordingCreate, AudioRecordingRead

router = APIRouter(
    prefix="/patients/{patient_id}/assessments/{assessment_id}/recordings",
    tags=["recordings"],
)

# where on disk we save files
UPLOAD_DIR = os.getenv("AUDIO_UPLOAD_DIR", "uploads/recordings")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get(
    "/",
    response_model=list[AudioRecordingRead],
)
async def list_recordings(
    patient_id: int,
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_recordings_for_assessment(db, assessment_id)


@router.post(
    "/",
    response_model=AudioRecordingRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "",
    response_model=AudioRecordingRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def upload_recording(
    patient_id: int,
    assessment_id: int,
    # the actual file
    file: UploadFile = File(...),
    # pull these two out of the same multipart form
    task_type: str = Form(..., title="Test Name"),
    recording_device: str | None = Form(None, title="Recording Device"),
    db: AsyncSession = Depends(get_db),
):
    # save to disk
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_name)
    try:
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}",
        )

    # build the metadata object
    audio_in = AudioRecordingCreate(
        filename=file.filename,
        file_path=f"/uploads/recordings/{unique_name}",
        recording_date=datetime.now(timezone.utc),
        task_type=task_type,
        recording_device=recording_device,
    )

    # insert into DB
    try:
        db_obj = await create_audio_recording(db, assessment_id, audio_in)
    except Exception as e:
        # if DB write fails, remove the file we just wrote
        os.remove(dest_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create audio record: {e}",
        )

    return db_obj


@router.delete(
    "/{recording_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recording_endpoint(
    patient_id: int,
    assessment_id: int,
    recording_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a recording by its ID.
    """
    from app.crud.audio_crud import get_recording
    
    try:
        # Get the recording first to get the file path
        recording = await get_recording(db, recording_id)
        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recording not found"
            )
        
        # Delete from database
        await delete_recording(db, recording_id)
        
        # Try to delete the physical file
        try:
            file_path = recording.file_path
            if file_path.startswith('/uploads/recordings/'):
                # Remove the leading slash to get relative path from current directory
                relative_path = file_path[1:]  # Remove leading '/'
                full_path = relative_path  # Use relative path directly
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"Successfully deleted file: {full_path}")
                else:
                    print(f"File not found for deletion: {full_path}")
            else:
                # Handle absolute paths or other formats
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Successfully deleted file: {file_path}")
        except Exception as file_error:
            print(f"Warning: Could not delete file {recording.file_path}: {file_error}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete recording: {e}",
        )