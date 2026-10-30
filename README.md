# NeuroCapture

A desktop platform for collecting and analyzing data in studies of neurodegenerative disease. It records standardized speech samples, scores cognitive tests (MMSE and MoCA), extracts 150+ acoustic features from each recording, and exports everything as analysis-ready CSV.

I built it to support a study run by the Center for Microsystems and Biodesign at Tecnológico de Monterrey, and wrote all of it: the database schema, the FastAPI backend, the audio feature pipeline and the Electron app.

## Why

Speech-based screening research needs recordings and cognitive scores that are collected the same way every time and linked to the right participant, followed by hundreds of features per recording. Doing that with loose audio files and spreadsheets is slow and error-prone. NeuroCapture puts collection, scoring, feature extraction and export in one tool.

## Features

**Participants**
- Study identifiers instead of names, plus demographics (age, gender, education).
- Referential integrity: assessments, recordings and features are linked to their participant with foreign keys and cascade deletes.

**Cognitive assessments**
- MMSE (30 points, 11 subscales) and MoCA (30 points, 8 domains), with subscores stored per domain.
- Custom assessments with their own scoring and subscales.

**Speech recording and analysis**
- Preprocessing: noise reduction, normalization and peak removal.
- WebRTC voice activity detection to separate speech from silence.
- 150+ features per recording:
  - *Voice quality:* jitter, shimmer, CPPS, HNR.
  - *Formants:* F1 to F4 statistics and bandwidths.
  - *Spectral:* 30 MFCCs and their deltas, spectral centroid, rolloff, flux and slope.
  - *Timing and rhythm:* speech and pause durations, pause counts, articulation rate, PVI rhythm indices, energy and intensity peaks.
  - *Complexity:* Higuchi fractal dimension and entropy measures.

**Export**
- One CSV with participant information, assessment scores and subscores, and all audio features, ready for statistical analysis.

## Architecture

```
Electron + React (Tailwind)  <-->  FastAPI (async SQLAlchemy)  <-->  PostgreSQL
                                          |
                                          v
                                  audio files on disk
```

- **Backend:** FastAPI with async SQLAlchemy and Pydantic schemas, Alembic migrations, and an audio processing service built on librosa, Praat (parselmouth) and WebRTC VAD.
- **Frontend:** Electron desktop app with a React and Tailwind interface.
- **Tests:** pytest suites for participants, assessments and recordings.

## Quick start

Requirements: Node.js 18+, Python 3.8+, Docker.

```bash
git clone https://github.com/MarcosSaade/NeuroCapture
cd NeuroCapture
docker-compose up -d db                 # PostgreSQL

cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install
npm run dev                             # launches the Electron app
```

The API runs at http://localhost:8000 with interactive docs at http://localhost:8000/docs.

Backend configuration goes in `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://neuro:capture@localhost:5432/neurocapture
UPLOAD_DIRECTORY=uploads
DEBUG=true
```

Run the tests with `pytest` from `backend/`.

## Project structure

```
backend/
  app/
    main.py          FastAPI application
    models.py        database models
    api/v1/          endpoints (participants, assessments, recordings, audio processing, export)
    services/        audio processing and feature extraction
    schemas/         Pydantic models
  alembic/           migrations
  tests/
frontend/
  main/              Electron main process
  renderer/          React app
docker-compose.yml   development database
```

Further documentation: [DOCUMENTATION.md](DOCUMENTATION.md), [API.md](API.md), [DEVELOPMENT.md](DEVELOPMENT.md), [DEPLOYMENT.md](DEPLOYMENT.md).

## Status and roadmap

Speech recording, cognitive assessments, feature extraction and export are implemented. The database schema already includes tables for accelerometer and OpenPose data and for model predictions, but their capture and analysis are not built yet. Planned:

- Accelerometer-based gait analysis.
- OpenPose pose estimation.
- Screening models trained on the collected features.

## License

MIT, see [LICENSE.txt](LICENSE.txt).
