import pytest
from httpx import AsyncClient # Changed from TestClient
from sqlalchemy.ext.asyncio import AsyncSession
# app.main is not directly needed for TestClient, but good for context
# from app.main import app 
from app.models import Patient, Assessment, AudioRecording # Added AudioRecording
from io import BytesIO

# client and db_session fixtures are expected to be in conftest.py

# Helper function to create patient and assessment for the test
async def create_patient_and_assessment(db: AsyncSession):
    patient = Patient(name="Test Patient", age=30) # Removed id, as it's auto-generated
    db.add(patient)
    await db.commit()
    await db.refresh(patient)

    assessment = Assessment(patient_id=patient.id, type="Test Assessment", date="2024-01-01") # Removed id
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return patient, assessment

@pytest.mark.asyncio
async def test_upload_recording_with_trailing_slash(client: AsyncClient, db_session: AsyncSession): # Changed client type hint
    # 1. Create mock patient and assessment
    patient, assessment = await create_patient_and_assessment(db_session)

    # 2. Construct URL with trailing slash
    # The prefix in recordings.py is "/patients/{patient_id}/assessments/{assessment_id}/recordings/"
    # The client base_url is "http://test", so the full URL for the client will be relative to that.
    # The router is mounted under /api/v1 in main.py's app router.
    # So the full path should be /api/v1/patients/{patient_id}/assessments/{assessment_id}/recordings/
    url = f"/api/v1/patients/{patient.id}/assessments/{assessment.id}/recordings/"

    # 3. Create mock audio file and form data
    mock_audio_content = b"fake audio data"
    # For httpx.AsyncClient, files are passed as a dict like {'file': (filename, content, content_type)}
    files = {"file": ("test_audio.wav", BytesIO(mock_audio_content), "audio/wav")}
    data = {"task_type": "Test Task"}

    # 4. Send POST request
    response = await client.post(url, files=files, data=data) # Added await

    # 5. Assert status code
    assert response.status_code == 201, response.text
    
    # Optional: Add more assertions, e.g., check response content or database state
    response_data = response.json()
    assert response_data["filename"] == "test_audio.wav"
    assert response_data["task_type"] == "Test Task"
    assert "id" in response_data
    assert response_data["assessment_id"] == assessment.id

    # Verify that the recording was actually saved to the database
    recording_id = response_data["id"]
    recording_in_db = await db_session.get(AudioRecording, recording_id)
    assert recording_in_db is not None
    assert recording_in_db.filename == "test_audio.wav"
    assert recording_in_db.task_type == "Test Task"
    assert recording_in_db.assessment_id == assessment.id
    assert recording_in_db.patient_id == patient.id # Check patient_id as well
    assert recording_in_db.url is not None # Ensure URL is populated
    # The URL in the DB should not contain the /api/v1 prefix, but the actual storage path
    # For now, just checking it's not None. The exact format depends on storage logic.
    # Example: "patient_1/assessment_1/test_audio.wav"
    expected_url_part = f"patient_{patient.id}/assessment_{assessment.id}/test_audio.wav"
    assert expected_url_part in recording_in_db.url
    # Clean up: delete the recording if necessary, though test DB is session-scoped
    # No explicit cleanup needed due to session-scoped DB from conftest.py
    # await db_session.delete(recording_in_db)
    # await db_session.commit()
    # No need to delete patient/assessment, as the DB is session-scoped and will be rolled back/dropped.
    # Patient and Assessment are created with auto-incrementing IDs.
    # The AudioRecording model will also have patient_id and assessment_id.
    # The create_recording function in crud/audio_crud.py populates these.
    # The response schema AudioRecordingRead includes patient_id.
    assert response_data["patient_id"] == patient.id
    # The path to the file is generated in audio_crud.py as:
    # file_path = f"patient_{patient_id}/assessment_{assessment_id}/{file.filename}"
    # This is stored in the 'url' field of AudioRecording.
    # The response schema uses 'url' for this path.
    assert response_data["url"] == f"patient_{patient.id}/assessment_{assessment.id}/test_audio.wav"

```
