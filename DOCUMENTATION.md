# NeuroCapture - Complete Project Documentation

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [File Structure Guide](#file-structure-guide)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Audio Processing Pipeline](#audio-processing-pipeline)
- [Frontend Components](#frontend-components)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Project Overview

NeuroCapture is a comprehensive neurological assessment platform that combines:
- **Cognitive Assessment Tools**: MMSE, MoCA, and custom evaluations
- **Audio Analysis**: Advanced speech feature extraction and processing
- **Multi-modal Data Collection**: Ready for accelerometer and OpenPose integration
- **Research-Grade Data Export**: CSV exports for statistical analysis

### Key Features
- Desktop application built with Electron + React
- RESTful API backend with FastAPI
- PostgreSQL database with comprehensive schema
- Real-time audio processing with 150+ acoustic features
- Modern, responsive UI with TailwindCSS

## Architecture

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Electron      │    │     FastAPI      │    │   PostgreSQL    │
│   Frontend      │◄──►│     Backend      │◄──►│    Database     │
│   (React)       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   File Storage   │
                       │  (Audio Files)   │
                       └──────────────────┘
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with AsyncPG driver
- **ORM**: SQLAlchemy (async)
- **Audio Processing**: librosa, parselmouth, noisereduce
- **Signal Processing**: scipy, numpy
- **Voice Activity Detection**: webrtcvad

#### Frontend
- **Framework**: React 18
- **Desktop App**: Electron
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **Icons**: HeroIcons

#### Infrastructure
- **Containerization**: Docker Compose
- **Database Migrations**: Alembic
- **Development**: Hot reload for both frontend and backend

## Setup and Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Docker and Docker Compose
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/MarcosSaade/NeuroCapture
   cd NeuroCapture
   ```

2. **Start the database**
   ```bash
   docker-compose up -d db
   ```

3. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Run migrations
   alembic upgrade head
   
   # Start the API server
   uvicorn app.main:app --reload --port 8000
   ```

4. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   
   # Development mode (hot reload)
   npm run dev
   
   # Or production build
   npm run build
   npm run start:electron
   ```

### Environment Configuration

Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql+asyncpg://neuro:capture@localhost:5432/neurocapture
UPLOAD_DIRECTORY=uploads
```

## File Structure Guide

### Backend Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py              # SQLAlchemy database models
│   ├── api/v1/endpoints/      # API route handlers
│   │   ├── patients.py        # Patient management endpoints
│   │   ├── demographics.py    # Demographic data endpoints
│   │   ├── assessments.py     # Cognitive assessment endpoints
│   │   ├── recordings.py      # Audio recording endpoints
│   │   ├── audio_processing.py # Audio processing task endpoints
│   │   ├── features.py        # Feature extraction endpoints
│   │   └── export.py          # Data export endpoints
│   ├── crud/                  # Database operations
│   ├── schemas/               # Pydantic models for validation
│   ├── services/              # Business logic services
│   │   ├── audio_processing.py # Audio analysis algorithms
│   │   └── task_manager.py    # Background task management
│   └── core/
│       └── database.py        # Database connection setup
├── alembic/                   # Database migration files
├── tests/                     # Unit and integration tests
├── uploads/recordings/        # Audio file storage
└── requirements.txt           # Python dependencies
```

### Frontend Structure
```
frontend/
├── main/
│   ├── index.js              # Electron main process
│   └── preload.js            # Electron preload script
├── renderer/
│   ├── src/
│   │   ├── App.jsx           # Main React application
│   │   ├── components/       # Reusable React components
│   │   │   ├── PatientTable.jsx      # Patient list table
│   │   │   ├── PatientDetail.jsx     # Patient detail modal
│   │   │   ├── AudioRecording.jsx    # Audio upload/playback
│   │   │   ├── AssessmentForm.jsx    # Cognitive assessment forms
│   │   │   └── Toast.jsx             # Notification system
│   │   ├── pages/            # Page-level components
│   │   ├── context/          # React context providers
│   │   ├── services/         # API service functions
│   │   └── utils/            # Utility functions
│   ├── index.html            # HTML template
│   └── vite.config.js        # Vite build configuration
└── package.json              # Node.js dependencies
```

## API Documentation

### Base URL
- Development: `http://localhost:8000`
- API Base Path: `/api/v1`

### Core Endpoints

#### Patients
- `GET /api/v1/patients` - List all patients
- `POST /api/v1/patients` - Create new patient
- `GET /api/v1/patients/{patient_id}` - Get patient details
- `PUT /api/v1/patients/{patient_id}` - Update patient
- `DELETE /api/v1/patients/{patient_id}` - Delete patient

#### Demographics
- `POST /api/v1/patients/{patient_id}/demographics` - Add demographic data
- `PUT /api/v1/demographics/{demographic_id}` - Update demographics

#### Cognitive Assessments
- `POST /api/v1/patients/{patient_id}/assessments` - Create assessment
- `GET /api/v1/assessments/{assessment_id}` - Get assessment details
- `PUT /api/v1/assessments/{assessment_id}` - Update assessment
- `DELETE /api/v1/assessments/{assessment_id}` - Delete assessment

#### Audio Processing
- `POST /api/v1/assessments/{assessment_id}/recordings` - Upload audio
- `POST /api/v1/recordings/{recording_id}/extract-features` - Extract features
- `GET /api/v1/tasks/{task_id}/progress` - Check processing progress

#### Data Export
- `GET /api/v1/export/features` - Export all features as CSV
- `GET /api/v1/export/patients` - Export patient data

### Response Formats

All API responses follow this structure:
```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Description of the operation"
}
```

Error responses include detailed error information:
```json
{
  "status": "error",
  "detail": "Specific error message",
  "type": "validation_error|not_found|server_error"
}
```

## Database Schema

### Core Tables

#### patients
Primary table for study participants
- `patient_id` (PK): Auto-incrementing integer
- `study_identifier`: Unique study ID (1-50 chars)
- `created_at`, `updated_at`: Timestamps

#### demographics
Participant demographic information
- `demographic_id` (PK): Auto-incrementing integer
- `patient_id` (FK): References patients table
- `age`: Participant age
- `gender`: Gender identification
- `education_years`: Years of formal education
- `collection_date`: Date of data collection

#### cognitive_assessments
Cognitive evaluation records
- `assessment_id` (PK): Auto-incrementing integer
- `patient_id` (FK): References patients table
- `assessment_type`: MMSE, MoCA, or Other
- `score`: Total assessment score
- `max_possible_score`: Maximum possible score
- `assessment_date`: Date and time of assessment
- `diagnosis`: Optional diagnostic information
- `notes`: Clinical notes

#### assessment_subscores
Detailed subscale scores for cognitive assessments
- `subscore_id` (PK): Auto-incrementing integer
- `assessment_id` (FK): References cognitive_assessments
- `name`: Subscale name (e.g., "Orientation", "Memory")
- `score`: Subscale score
- `max_score`: Maximum possible subscale score

#### audio_recordings
Audio file metadata and associations
- `recording_id` (PK): Auto-incrementing integer
- `assessment_id` (FK): References cognitive_assessments
- `file_path`: Server file path
- `filename`: Original filename
- `recording_date`: Recording timestamp
- `recording_device`: Device used for recording
- `task_type`: Type of cognitive task

#### audio_features
Extracted acoustic features from audio recordings
- `feature_id` (PK): Auto-incrementing integer
- `recording_id` (FK): References audio_recordings
- `feature_name`: Name of the acoustic feature
- `feature_value`: Numeric value of the feature

### Future Tables (Prepared)

#### accelerometer_data / accelerometer_readings
For motion capture data collection

#### openpose_data / openpose_keypoints
For pose estimation and gesture analysis

#### interpretations
For clinical interpretations and notes

#### model_predictions
For machine learning model outputs

### Relationships and Constraints

- **Cascade Deletes**: Deleting a patient removes all associated data
- **Foreign Key Constraints**: Maintain referential integrity
- **Unique Constraints**: Prevent duplicate study identifiers
- **Timestamp Triggers**: Automatic update of timestamp fields

## Audio Processing Pipeline

### Overview
The audio processing system extracts 150+ acoustic features from speech recordings through a multi-stage pipeline.

### Processing Stages

#### 1. Preprocessing
```python
def preprocess_audio(file_path: str) -> np.ndarray:
    """
    Complete audio preprocessing pipeline:
    1. Load and convert to 16kHz mono
    2. Normalize RMS levels
    3. Reduce background noise
    4. Remove extreme amplitude peaks
    """
```

#### 2. Voice Activity Detection (VAD)
```python
def detect_voice_activity(audio_data: np.ndarray, sr: int) -> List[Tuple[float, float]]:
    """
    Identify speech vs silence segments using WebRTC VAD:
    - Converts to required sample rate (8kHz/16kHz)
    - Applies configurable aggressiveness levels
    - Returns list of (start_time, end_time) tuples
    """
```

#### 3. Feature Extraction

##### Prosodic Features (35+ features)
- **Temporal Features**: Speech duration, pause counts, speech rate
- **Energy Features**: Short-time energy, energy variability
- **Rhythm Features**: PVI (Pairwise Variability Index), tempo estimation
- **Peak Features**: Intensity peaks, inter-peak intervals

##### Acoustic Features (150+ features)

**Voice Quality:**
- Jitter (local, PPQ5): Frequency stability measures
- Shimmer (local, APQ5): Amplitude stability measures
- CPPS: Cepstral Peak Prominence Smoothed

**Formant Analysis:**
- F1-F4 formants: Statistical measures (mean, std, range, median)
- Formant bandwidths and variability
- Delta formants (temporal derivatives)

**Spectral Features:**
- 30 MFCCs with delta and delta-delta coefficients
- Spectral centroid, rolloff, flux
- Zero-crossing rate, spectral slope
- Harmonic-to-noise ratio (HNR)

**Complexity Measures:**
- Higuchi Fractal Dimension (HFD): Signal complexity
- Multiple window sizes for robust analysis

### Feature Validation and Storage

```python
def validate_and_store_features(features: Dict[str, float], recording_id: int):
    """
    Validates extracted features and stores in database:
    - Filters out NaN and infinite values
    - Logs feature extraction statistics
    - Stores valid features in audio_features table
    """
```

### Background Processing

The system uses asynchronous task processing for audio analysis:

1. **Task Creation**: User uploads audio → Task queued
2. **Progress Tracking**: Real-time progress updates (0-100%)
3. **Feature Storage**: Valid features saved to database
4. **File Management**: Processed audio files saved with "_cleaned" suffix

## Frontend Components

### Component Architecture

#### Core Components

**App.jsx**
- Main application container
- Routing configuration
- Global state management
- Modal orchestration

**PatientTable.jsx**
- Patient list with search and filtering
- Pagination and sorting
- Action buttons (edit, delete, view)
- Real-time updates

**PatientDetail.jsx**
- Tabbed interface for patient data
- Demographics, assessments, and audio tabs
- Inline editing capabilities
- Deletion confirmations

**AssessmentForm.jsx**
- Dynamic forms for MMSE, MoCA, and custom assessments
- Automatic subscale calculation
- Validation and error handling
- Date/time picking

**AudioRecording.jsx**
- Audio file upload with drag-and-drop
- Audio playback controls
- Feature extraction progress tracking
- Processing status indicators

#### Utility Components

**Modal.jsx**
- Reusable modal wrapper
- Multiple size options
- Backdrop click handling
- ESC key support

**Toast.jsx**
- Notification system
- Success, error, and info messages
- Auto-dismiss functionality
- Queue management

**ConfirmDialog.jsx**
- Confirmation dialogs for destructive actions
- Customizable messages and actions
- Keyboard navigation

### State Management

#### Context Providers

**NotificationContext**
- Global notification state
- Toast message queue
- Auto-dismiss timers

**PatientContext** (if implemented)
- Current patient state
- Assessment data
- Audio processing status

### API Integration

#### Service Layer
```javascript
// services/api.js
const API_BASE = 'http://localhost:8000/api/v1';

export const patientService = {
  getAll: () => axios.get(`${API_BASE}/patients`),
  create: (data) => axios.post(`${API_BASE}/patients`, data),
  update: (id, data) => axios.put(`${API_BASE}/patients/${id}`, data),
  delete: (id) => axios.delete(`${API_BASE}/patients/${id}`)
};
```

#### Error Handling
- Consistent error response processing
- User-friendly error messages
- Network error recovery
- Retry mechanisms for failed requests

## Development Workflow

### Code Standards

#### Python (Backend)
- **PEP 8**: Standard Python style guide
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Error Handling**: Comprehensive try-catch blocks

#### JavaScript/React (Frontend)
- **ES6+**: Modern JavaScript features
- **Functional Components**: Prefer hooks over class components
- **PropTypes**: Type checking for component props
- **Consistent Naming**: camelCase for variables, PascalCase for components

### Git Workflow

#### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature development
- `hotfix/*`: Critical bug fixes

#### Commit Messages
```
type(scope): description

feat(audio): add formant analysis pipeline
fix(api): resolve patient deletion cascade issue
docs(readme): update installation instructions
```

### Database Migrations

#### Creating Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

#### Migration Best Practices
- Always review auto-generated migrations
- Test migrations on development data
- Include both upgrade and downgrade scripts
- Document complex migration logic

## Testing

### Backend Testing

#### Test Structure
```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── test_patients.py      # Patient CRUD operations
├── test_assessments.py   # Assessment functionality
├── test_recordings.py    # Audio recording tests
└── test_audio_processing.py  # Feature extraction tests
```

#### Running Tests
```bash
pytest
```

#### Test Fixtures
- **Database**: Isolated test database
- **Sample Data**: Realistic test datasets
- **Mock Services**: External service mocking

### Frontend Testing

#### Testing Tools
- **Jest**: JavaScript testing framework
- **React Testing Library**: Component testing
- **MSW**: API mocking
- **Electron Testing**: End-to-end testing

#### Test Categories
- **Unit Tests**: Individual component behavior
- **Integration Tests**: Component interaction
- **E2E Tests**: Full user workflows

## Deployment

### Production Deployment

#### Backend Deployment
1. **Environment Setup**
   ```bash
   # Production environment variables
   DATABASE_URL=postgresql://user:pass@prod-db:5432/neurocapture
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create initial admin user (if applicable)
   python scripts/create_admin.py
   ```

3. **Server Configuration**
   ```bash
   # Production server with gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

#### Frontend Deployment
```bash
# Build for production
npm run build:renderer

# Package as desktop app
npm run build:electron

# Create installer (platform-specific)
npm run dist
```

### Docker Deployment

#### Complete Stack
```yaml
# docker-compose.prod.yml
version: "3.9"
services:
  app:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://neuro:capture@db:5432/neurocapture
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: neuro
      POSTGRES_PASSWORD: capture
      POSTGRES_DB: neurocapture
    volumes:
      - prod_db_data:/var/lib/postgresql/data
      
volumes:
  prod_db_data:
```

### Performance Optimization

#### Backend Optimizations
- **Database Indexing**: Optimize frequent queries
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis for frequent data access
- **Background Tasks**: Celery for heavy processing

#### Frontend Optimizations
- **Code Splitting**: Load components on demand
- **Bundle Optimization**: Minimize JavaScript bundle size
- **Image Optimization**: Compress and lazy-load images
- **Memoization**: React.memo for expensive components

## Troubleshooting

### Common Issues

#### Database Connection Errors
```
Error: could not connect to server: Connection refused
```
**Solution**: Ensure PostgreSQL is running and connection parameters are correct
```bash
docker-compose up -d db
```

#### Audio Processing Failures
```
Error: Unable to extract features from audio file
```
**Solutions**:
- Check audio file format (supported: wav, mp3, flac)
- Verify file is not corrupted
- Ensure sufficient disk space for temporary files

#### Electron App Won't Start
```
Error: Cannot find module 'electron'
```
**Solution**: Reinstall dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Performance Issues

#### Slow Feature Extraction
- **Cause**: Large audio files or complex analysis
- **Solution**: Implement progress chunking and user feedback

#### Database Query Slowdowns
- **Cause**: Missing indexes on frequently queried columns
- **Solution**: Add database indexes
```sql
CREATE INDEX idx_patients_study_identifier ON patients(study_identifier);
CREATE INDEX idx_audio_features_recording_id ON audio_features(recording_id);
```

### Debugging Tips

#### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add breakpoints
import pdb; pdb.set_trace()
```

#### Frontend Debugging
```javascript
// React Developer Tools
// Browser console logging
console.log('Debug info:', data);

// Network tab for API calls
// Performance tab for rendering issues
```

### Log Analysis

#### Backend Logs
- **Location**: Console output or log files
- **Format**: Structured JSON logs
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### Frontend Logs
- **Browser Console**: JavaScript errors and warnings
- **Electron Logs**: Main process and renderer logs
- **Network Logs**: API request/response debugging

---

## Contact and Support

For technical support or questions about the codebase:
- Review this documentation first
- Contact snavarro.tuch@tec.mx

**Project Status**: Production-ready beta
**Last Updated**: June 2025
**Maintainer**: Center For Microsystems and Biodesign, Tecnológico de Monterrey
