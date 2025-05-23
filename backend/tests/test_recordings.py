import pytest
import io
import os
from datetime import datetime, timezone
from httpx import AsyncClient

# Helper function (to be included in backend/tests/test_recordings.py if not shared)
def parse_iso_datetime_str(datetime_str: str) -> datetime:
    if datetime_str and datetime_str.endswith("Z"):
        datetime_str = datetime_str[:-1] + "+00:00"
    dt = datetime.fromisoformat(datetime_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

@pytest.mark.asyncio
async def test_upload_audio_recording(client: AsyncClient, test_patient: dict):
    # 1. Create an Assessment
    patient_id = test_patient["patient_id"]
    assessment_data = {
        "assessment_type": "Test Assessment",
        "score": 10,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post(
        f"/api/v1/patients/{patient_id}/assessments/", json=assessment_data
    )
    assert response.status_code == 201
    assessment_response_data = response.json()
    assessment_id = assessment_response_data["assessment_id"]

    # 2. Prepare Upload Data
    task_type = "Test Speech Task"
    recording_device = "Test Microphone"
    filename = "test_audio.wav"
    dummy_audio_content = b"dummy audio data"
    dummy_file_object = io.BytesIO(dummy_audio_content)

    # 3. Perform Upload
    upload_url = f"/api/v1/patients/{patient_id}/assessments/{assessment_id}/recordings/"
    files = {"file": (filename, dummy_file_object, "audio/wav")}
    data = {"task_type": task_type, "recording_device": recording_device}
    
    response = await client.post(upload_url, files=files, data=data)

    # 4. Assert Response
    assert response.status_code == 201
    response_data = response.json()

    assert response_data["filename"] == filename
    assert response_data["task_type"] == task_type
    assert response_data["recording_device"] == recording_device
    assert response_data["assessment_id"] == assessment_id
    
    assert response_data["file_path"].startswith("/uploads/recordings/")
    assert response_data["file_path"].endswith(".wav")
    
    # Check for UUID-like name in the path (e.g., it's not just /uploads/recordings/test_audio.wav)
    path_parts = response_data["file_path"].split('/')
    assert len(path_parts) == 4  # e.g. ['', 'uploads', 'recordings', '<uuid>.wav']
    assert path_parts[3] != filename # The server generates a unique name
    assert len(path_parts[3]) > len(filename) # UUID part should make it longer

    # Validate datetime strings
    assert isinstance(parse_iso_datetime_str(response_data["recording_date"]), datetime)
    assert isinstance(parse_iso_datetime_str(response_data["created_at"]), datetime)
    assert isinstance(parse_iso_datetime_str(response_data["updated_at"]), datetime)
