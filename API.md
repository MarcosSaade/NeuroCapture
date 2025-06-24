# NeuroCapture API Reference

Complete reference for the NeuroCapture RESTful API endpoints.

## Base Information

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **API Prefix**: `/api/v1`
- **Content Type**: `application/json`
- **Authentication**: None (internal desktop application)

## Response Format

All API responses follow a consistent structure:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "detail": "Error description",
  "type": "error_type"
}
```

### HTTP Status Codes
- `200` - OK (successful GET, PUT)
- `201` - Created (successful POST)
- `204` - No Content (successful DELETE)
- `400` - Bad Request (validation error)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (validation error with details)
- `500` - Internal Server Error

## Patient Management

### List Patients
Get paginated list of all patients.

**Endpoint**: `GET /api/v1/patients`

**Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Example Request**:
```http
GET /api/v1/patients?skip=0&limit=50
```

**Example Response**:
```json
[
  {
    "patient_id": 1,
    "study_identifier": "STUDY001",
    "created_at": "2025-06-01T10:00:00Z",
    "updated_at": "2025-06-01T10:00:00Z"
  },
  {
    "patient_id": 2,
    "study_identifier": "STUDY002", 
    "created_at": "2025-06-02T11:30:00Z",
    "updated_at": "2025-06-02T11:30:00Z"
  }
]
```

### Get Patient
Retrieve specific patient by ID.

**Endpoint**: `GET /api/v1/patients/{patient_id}`

**Parameters**:
- `patient_id` (path): Patient ID

**Example Request**:
```http
GET /api/v1/patients/1
```

**Example Response**:
```json
{
  "patient_id": 1,
  "study_identifier": "STUDY001",
  "created_at": "2025-06-01T10:00:00Z",
  "updated_at": "2025-06-01T10:00:00Z"
}
```

### Create Patient
Create new patient record.

**Endpoint**: `POST /api/v1/patients`

**Request Body**:
```json
{
  "study_identifier": "STUDY003"
}
```

**Validation Rules**:
- `study_identifier`: 1-50 characters, must be unique

**Example Response**:
```json
{
  "patient_id": 3,
  "study_identifier": "STUDY003",
  "created_at": "2025-06-24T15:30:00Z",
  "updated_at": "2025-06-24T15:30:00Z"
}
```

### Update Patient
Update patient information.

**Endpoint**: `PUT /api/v1/patients/{patient_id}`

**Request Body**:
```json
{
  "study_identifier": "STUDY003_UPDATED"
}
```

**Example Response**:
```json
{
  "patient_id": 3,
  "study_identifier": "STUDY003_UPDATED",
  "created_at": "2025-06-24T15:30:00Z",
  "updated_at": "2025-06-24T16:00:00Z"
}
```

### Delete Patient
Delete patient and all associated data.

**Endpoint**: `DELETE /api/v1/patients/{patient_id}`

**Response**: `204 No Content`

**Note**: This operation cascades to delete:
- Demographics
- Cognitive assessments and subscores
- Audio recordings and features

## Demographics

### Create Demographics
Add demographic information for a patient.

**Endpoint**: `POST /api/v1/patients/{patient_id}/demographics`

**Request Body**:
```json
{
  "age": 65,
  "gender": "Female",
  "education_years": 16,
  "collection_date": "2025-06-24"
}
```

**Validation Rules**:
- `age`: Positive integer
- `gender`: Non-empty string
- `education_years`: Optional positive integer
- `collection_date`: Valid date in YYYY-MM-DD format

**Example Response**:
```json
{
  "demographic_id": 1,
  "patient_id": 1,
  "age": 65,
  "gender": "Female",
  "education_years": 16,
  "collection_date": "2025-06-24",
  "created_at": "2025-06-24T15:30:00Z",
  "updated_at": "2025-06-24T15:30:00Z"
}
```

### Update Demographics
Update demographic information.

**Endpoint**: `PUT /api/v1/demographics/{demographic_id}`

**Request Body**: Same as create demographics

## Cognitive Assessments

### Create Assessment
Create new cognitive assessment.

**Endpoint**: `POST /api/v1/patients/{patient_id}/assessments`

**Request Body**:
```json
{
  "assessment_date": "2025-06-24T15:30:00Z",
  "assessment_type": "MMSE",
  "score": 28.0,
  "max_possible_score": 30.0,
  "diagnosis": "Mild Cognitive Impairment",
  "duration_total_minutes": 15,
  "notes": "Patient showed some difficulty with delayed recall tasks."
}
```

**Assessment Types**:
- `MMSE`: Mini-Mental State Examination
- `MoCA`: Montreal Cognitive Assessment  
- `Other`: Custom assessment

**Example Response**:
```json
{
  "assessment_id": 1,
  "patient_id": 1,
  "assessment_date": "2025-06-24T15:30:00Z",
  "assessment_type": "MMSE",
  "score": 28.0,
  "max_possible_score": 30.0,
  "diagnosis": "Mild Cognitive Impairment",
  "duration_total_minutes": 15,
  "notes": "Patient showed some difficulty with delayed recall tasks.",
  "created_at": "2025-06-24T15:35:00Z",
  "updated_at": "2025-06-24T15:35:00Z"
}
```

### Get Assessment
Retrieve assessment details.

**Endpoint**: `GET /api/v1/assessments/{assessment_id}`

### Update Assessment
Update assessment information.

**Endpoint**: `PUT /api/v1/assessments/{assessment_id}`

### Delete Assessment
Delete assessment and associated data.

**Endpoint**: `DELETE /api/v1/assessments/{assessment_id}`

## Assessment Subscores

### Create Subscores
Add detailed subscale scores for an assessment.

**Endpoint**: `POST /api/v1/assessments/{assessment_id}/subscores`

**Request Body** (MMSE example):
```json
[
  {
    "name": "Orientation to Time",
    "score": 4.0,
    "max_score": 5.0
  },
  {
    "name": "Orientation to Place", 
    "score": 5.0,
    "max_score": 5.0
  },
  {
    "name": "Registration",
    "score": 3.0,
    "max_score": 3.0
  }
]
```

**MoCA Domains**:
- Visuospatial/Executive
- Naming
- Memory
- Attention
- Language
- Abstraction
- Delayed Recall
- Orientation

### Get Subscores
Retrieve subscores for an assessment.

**Endpoint**: `GET /api/v1/assessments/{assessment_id}/subscores`

### Update Subscore
Update individual subscore.

**Endpoint**: `PUT /api/v1/subscores/{subscore_id}`

### Delete Subscore
Delete individual subscore.

**Endpoint**: `DELETE /api/v1/subscores/{subscore_id}`

## Audio Recordings

### Upload Audio Recording
Upload audio file for an assessment.

**Endpoint**: `POST /api/v1/assessments/{assessment_id}/recordings`

**Content Type**: `multipart/form-data`

**Form Fields**:
- `file`: Audio file (WAV, MP3, FLAC)
- `recording_device` (optional): Recording device name
- `task_type` (optional): Type of cognitive task

**Example Response**:
```json
{
  "recording_id": 1,
  "assessment_id": 1,
  "file_path": "uploads/recordings/uuid-filename.wav",
  "filename": "patient_recording.wav",
  "recording_date": "2025-06-24T15:45:00Z",
  "recording_device": "iPhone 12",
  "task_type": "sentence reading",
  "created_at": "2025-06-24T15:45:00Z",
  "updated_at": "2025-06-24T15:45:00Z"
}
```

### Get Recording Details
Retrieve recording metadata.

**Endpoint**: `GET /api/v1/recordings/{recording_id}`

### List Assessment Recordings
Get all recordings for an assessment.

**Endpoint**: `GET /api/v1/assessments/{assessment_id}/recordings`

### Delete Recording
Delete recording and associated features.

**Endpoint**: `DELETE /api/v1/recordings/{recording_id}`

## Audio Processing

### Extract Features
Start feature extraction from audio recording.

**Endpoint**: `POST /api/v1/recordings/{recording_id}/extract-features`

**Response**:
```json
{
  "task_id": "uuid-task-id",
  "status": "pending",
  "message": "Feature extraction task started"
}
```

**Task Statuses**:
- `pending`: Task queued
- `running`: Currently processing
- `completed`: Successfully finished
- `failed`: Error occurred

### Check Task Progress
Monitor feature extraction progress.

**Endpoint**: `GET /api/v1/tasks/{task_id}/progress`

**Response**:
```json
{
  "task_id": "uuid-task-id",
  "status": "running",
  "progress": 65,
  "message": "Extracting formant features...",
  "features_extracted": 98,
  "total_features": 150
}
```

### Get Task Result
Retrieve completed task results.

**Endpoint**: `GET /api/v1/tasks/{task_id}/result`

**Response**:
```json
{
  "task_id": "uuid-task-id",
  "status": "completed",
  "result": {
    "features_extracted": 147,
    "features_failed": 3,
    "processing_time_seconds": 45.2,
    "cleaned_file_path": "uploads/recordings/uuid-filename_cleaned.wav"
  }
}
```

## Audio Features

### Get Recording Features
Retrieve all extracted features for a recording.

**Endpoint**: `GET /api/v1/recordings/{recording_id}/features`

**Response**:
```json
[
  {
    "feature_id": 1,
    "recording_id": 1,
    "feature_name": "total_duration_seconds",
    "feature_value": 32.5,
    "created_at": "2025-06-24T16:00:00Z"
  },
  {
    "feature_id": 2,
    "recording_id": 1,
    "feature_name": "speech_rate_syllables_per_second",
    "feature_value": 4.2,
    "created_at": "2025-06-24T16:00:00Z"
  }
]
```

### Feature Categories

**Prosodic Features** (35+ features):
- Temporal: `total_duration_seconds`, `speech_duration_seconds`, `pause_count`
- Energy: `energy_mean`, `energy_std`, `energy_cv`
- Rhythm: `pvi_raw`, `pvi_normalized`, `tempo_bpm`

**Acoustic Features** (150+ features):
- Voice Quality: `jitter_local`, `shimmer_local`, `cpps`, `hnr_mean`
- Formants: `f1_mean`, `f1_std`, `f2_mean`, `f2_std`, `f3_mean`, `f4_mean`
- Spectral: `mfcc_1_mean`, `mfcc_1_std`, `spectral_centroid_mean`
- Complexity: `hfd_mean`, `hfd_max`, `hfd_min`

## Data Export

### Export All Features
Export comprehensive feature dataset as CSV.

**Endpoint**: `GET /api/v1/export/features`

**Parameters**:
- `format` (optional): Export format (`csv` default)

**Response**: CSV file download

**CSV Structure**:
```csv
patient_id,study_identifier,assessment_id,assessment_type,recording_id,feature_name,feature_value
1,STUDY001,1,MMSE,1,total_duration_seconds,32.5
1,STUDY001,1,MMSE,1,speech_rate_syllables_per_second,4.2
```

### Export Patient Data
Export patient and demographic data.

**Endpoint**: `GET /api/v1/export/patients`

**Response**: CSV file with patient information

## Error Handling

### Common Error Responses

**Validation Error (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "study_identifier"],
      "msg": "ensure this value has at most 50 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {"limit_value": 50}
    }
  ]
}
```

**Not Found (404)**:
```json
{
  "detail": "Patient not found"
}
```

**Duplicate Entry (400)**:
```json
{
  "detail": "Study identifier already exists"
}
```

### Audio Processing Errors

**Unsupported Format**:
```json
{
  "detail": "Unsupported audio format. Please use WAV, MP3, or FLAC.",
  "type": "audio_format_error"
}
```

**Processing Failed**:
```json
{
  "detail": "Feature extraction failed: Unable to detect voice activity",
  "type": "audio_processing_error"
}
```

## Rate Limiting

Currently no rate limiting is implemented as this is a desktop application with direct database access.

## API Testing

### Using the Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI with:
- Interactive endpoint testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

### Using curl

**Create Patient**:
```bash
curl -X POST "http://localhost:8000/api/v1/patients" \
  -H "Content-Type: application/json" \
  -d '{"study_identifier": "TEST001"}'
```

**Upload Audio**:
```bash
curl -X POST "http://localhost:8000/api/v1/assessments/1/recordings" \
  -F "file=@recording.wav" \
  -F "recording_device=iPhone" \
  -F "task_type=sentence reading"
```

### Using Python requests

```python
import requests

# Create patient
response = requests.post(
    "http://localhost:8000/api/v1/patients",
    json={"study_identifier": "TEST001"}
)
patient = response.json()

# Upload audio
with open("recording.wav", "rb") as f:
    response = requests.post(
        f"http://localhost:8000/api/v1/assessments/1/recordings",
        files={"file": f},
        data={
            "recording_device": "iPhone", 
            "task_type": "sentence reading"
        }
    )
```

## WebSocket Support

Currently not implemented. All operations are synchronous HTTP requests with polling for task progress.

## API Versioning

- Current version: v1
- All endpoints prefixed with `/api/v1`
- Future versions will be available at `/api/v2`, etc.
- Backward compatibility maintained for at least one major version

---

For additional technical details, see [DOCUMENTATION.md](DOCUMENTATION.md).
