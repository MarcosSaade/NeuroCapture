# NeuroCapture

A comprehensive neurological assessment platform combining cognitive evaluations with advanced audio analysis for research and clinical applications.

## 🎯 Overview

NeuroCapture provides researchers and clinicians with a complete solution for:
- **Cognitive Assessment**: MMSE, MoCA, and custom evaluations
- **Speech Analysis**: 150+ acoustic features from audio recordings  
- **Data Management**: Secure patient data storage and export
- **Multi-modal Ready**: Prepared for accelerometer and pose analysis

## ✨ Key Features

### 🧠 Cognitive Assessments
- **MMSE (Mini-Mental State Examination)**: 30-point scale with 11 subscales
- **MoCA (Montreal Cognitive Assessment)**: 30-point scale with 8 domains
- **Custom Assessments**: Flexible scoring and subscale definitions
- **Detailed Subscores**: Domain-specific analysis for comprehensive evaluation

### 🎵 Audio Processing
- **Advanced Preprocessing**: Noise reduction, normalization, peak removal
- **Voice Activity Detection**: WebRTC-based speech/silence segmentation
- **Prosodic Features**: Timing, rhythm, energy, and tempo analysis
- **Acoustic Features**: Voice quality, formants, spectral characteristics
- **Complexity Measures**: Fractal dimension and entropy analysis

### 📊 Data Management
- **Patient Management**: Secure study identifier system
- **Demographics**: Age, gender, education, and custom fields
- **Export Capabilities**: CSV export for statistical analysis
- **Data Integrity**: Cascade deletes and referential constraints

### 🖥️ Modern Interface
- **Desktop Application**: Cross-platform Electron app
- **Responsive Design**: Modern UI with TailwindCSS
- **Real-time Feedback**: Progress tracking and notifications
- **Intuitive Navigation**: Tabbed interface with modal editing

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Electron      │    │     FastAPI      │    │   PostgreSQL    │
│   Frontend      │◄──►│     Backend      │◄──►│    Database     │
│   (React)       │    │   (Python)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   File Storage   │
                       │  (Audio Files)   │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+
- **Docker** and Docker Compose
- **Git**

### Installation

1. **Clone and setup database**
   ```bash
   git clone https://github.com/MarcosSaade/NeuroCapture
   cd NeuroCapture
   docker-compose up -d db
   ```

2. **Backend setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   npm run dev  # Development mode
   ```

4. **Access the application**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend: Launches automatically via Electron

## 📁 Project Structure

```
NeuroCapture/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── models.py       # Database models
│   │   ├── api/v1/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── schemas/        # Data validation
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/               # Electron frontend
│   ├── main/               # Electron main process
│   └── renderer/           # React application
├── docker-compose.yml      # Development database
├── DOCUMENTATION.md        # Complete technical docs
└── README.md              # This file
```

## 🔬 Audio Features

### Prosodic Features (35+)
- **Temporal**: Speech duration, pause counts, articulation rate
- **Energy**: Short-time energy analysis and variability
- **Rhythm**: PVI indices, tempo estimation, beat intervals
- **Peaks**: Intensity peaks and inter-peak statistics

### Acoustic Features (150+)
- **Voice Quality**: Jitter, shimmer, CPPS, HNR
- **Formants**: F1-F4 statistics, bandwidths, derivatives
- **Spectral**: 30 MFCCs, centroid, rolloff, flux, slope
- **Complexity**: Higuchi Fractal Dimension, entropy measures

## 🧪 Testing

```bash
pytest
```

## 📊 Data Export

Export comprehensive datasets in CSV format:
- **Patient Information**: Demographics and study identifiers
- **Assessment Results**: Scores, subscales, and clinical notes
- **Audio Features**: All extracted acoustic characteristics
- **Metadata**: Recording details and processing information

## 🔧 Configuration

### Environment Variables
Create `.env` in the backend directory:
```env
DATABASE_URL=postgresql+asyncpg://neuro:capture@localhost:5432/neurocapture
UPLOAD_DIRECTORY=uploads
DEBUG=true
```

### Database Configuration
Default PostgreSQL settings:
- **Host**: localhost:5432
- **Database**: neurocapture
- **User**: neuro
- **Password**: capture

## 🤝 Development Workflow

### Code Standards
- **Python**: PEP 8, type hints, comprehensive docstrings
- **JavaScript**: ES6+, functional components, JSDoc comments
- **Git**: Conventional commits, feature branches

### Making Changes
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and add tests
3. Run tests: `pytest` (backend) and `npm test` (frontend)
4. Commit: `git commit -m "feat(scope): description"`
5. Push and create pull request

## 📚 Documentation

- **[DOCUMENTATION.md](DOCUMENTATION.md)**: Complete technical documentation
- **[API Docs](http://localhost:8000/docs)**: Interactive API documentation
- **[ReDoc](http://localhost:8000/redoc)**: Alternative API documentation


## 🔮 Future Features

- **Accelerometer Analysis**: Motion and gait pattern analysis
- **OpenPose Integration**: Pose estimation and gesture analysis  
- **Machine Learning Models**: Automated diagnostic predictions
- **ENASEM Integration**: Specialized demographic fields

## 📄 License

This project is proprietary software developed at Tecnológico de Monterrey for research purposes.
For details, contact snavarro.tuch@tec.mx.

---

**Version**: 0.1.0  
**Last Updated**: June 2025  
**Status**: Production-ready beta
