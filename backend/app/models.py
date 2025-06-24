"""
NeuroCapture Database Models

SQLAlchemy models defining the database schema for the NeuroCapture platform.
Includes models for patient management, cognitive assessments, audio recordings,
feature storage, and future multi-modal data collection.

Key Features:
- Cascade deletes for data integrity
- Automatic timestamp management
- Comprehensive relationships
- Support for multi-modal data types

Author: NeuroCapture Development Team
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text,
    Date, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()

def utc_now():
    """Generate current UTC timestamp for database defaults."""
    return datetime.now(timezone.utc)


class Patient(Base):
    """
    Core patient/participant model for the study.
    
    Represents individual study participants with unique identifiers.
    Serves as the central entity linking all collected data types.
    
    Relationships:
    - One-to-many with Demographics, CognitiveAssessment
    - Future: AccelerometerData, OpenPoseData
    """
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    study_identifier = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships with cascade delete for data integrity
    demographics = relationship(
        "Demographic",
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    assessments = relationship(
        "CognitiveAssessment",
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # Future multi-modal data relationships
    accel_sessions = relationship("AccelerometerData", back_populates="patient")
    openpose_sessions = relationship("OpenPoseData", back_populates="patient")


class Demographic(Base):
    """
    Demographic information for study participants.
    
    Stores essential demographic data including age, gender, education,
    and collection metadata. Prepared for ENASEM study integration.
    
    Fields:
    - age: Participant age at time of assessment
    - gender: Gender identification (validated values)
    - education_years: Years of formal education (optional)
    - collection_date: Date when demographic data was collected
    """
    __tablename__ = "demographics"

    demographic_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    education_years = Column(Integer, nullable=True)
    collection_date = Column(Date, nullable=False)
    # TODO: Add ENASEM-specific fields as requirements are finalized
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="demographics")


class CognitiveAssessment(Base):
    """
    Cognitive assessment records for neurological evaluation.
    
    Supports multiple assessment types including MMSE, MoCA, and custom evaluations.
    Links to detailed subscores and associated audio recordings.
    
    Assessment Types:
    - MMSE: Mini-Mental State Examination (30 points max)
    - MoCA: Montreal Cognitive Assessment (30 points max)  
    - Other: Custom assessments with flexible scoring
    
    Features:
    - Automatic timestamp recording
    - Optional diagnostic information
    - Duration tracking
    - Clinical notes storage
    """
    __tablename__ = "cognitive_assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessment_type = Column(String(50), nullable=False, index=True)  # MMSE, MoCA, Other
    score = Column(Float, nullable=False)
    max_possible_score = Column(Float, nullable=True)
    diagnosis = Column(String(50), nullable=True)
    duration_total_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="assessments")
    audio_recordings = relationship(
        "AudioRecording", 
        back_populates="assessment",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    subscores = relationship(
        "AssessmentSubscore",
        back_populates="assessment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AssessmentSubscore(Base):
    """
    Detailed subscale scores for cognitive assessments.
    
    Stores individual domain/subscale scores for comprehensive assessment analysis.
    
    MMSE Subscales (11 total):
    - Orientation to Time, Orientation to Place, Registration, etc.
    
    MoCA Subscales (8 domains):
    - Visuospatial/Executive, Naming, Memory, Attention, etc.
    
    Custom assessments can define their own subscales.
    """
    __tablename__ = "assessment_subscores"

    subscore_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("cognitive_assessments.assessment_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = Column(String(100), nullable=False)  # Subscale name
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    assessment = relationship("CognitiveAssessment", back_populates="subscores")



class AudioRecording(Base):
    """
    Audio recording metadata and file management.
    
    Stores information about uploaded audio files associated with cognitive assessments.
    Links to extracted acoustic features and future AI model predictions.
    
    Supported Features:
    - Multiple audio formats (WAV, MP3, FLAC)
    - Recording device tracking
    - Task type classification
    - Automatic file path management
    """
    __tablename__ = "audio_recordings"

    recording_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer, 
        ForeignKey("cognitive_assessments.assessment_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    file_path = Column(String(255), nullable=False)
    filename = Column(String(100), nullable=False)
    recording_date = Column(DateTime(timezone=True), nullable=False)
    recording_device = Column(String(50), nullable=True)
    task_type = Column(String(100), nullable=True)  # e.g., "sentence reading", "spontaneous speech"
    
    # Future feature relationships
    interpretation_id = Column(Integer, ForeignKey("interpretations.interpretation_id"), nullable=True)
    prediction_id = Column(Integer, ForeignKey("model_predictions.prediction_id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    assessment = relationship("CognitiveAssessment", back_populates="audio_recordings")
    features = relationship(
        "AudioFeature", 
        back_populates="recording", 
        cascade="all, delete-orphan", 
        passive_deletes=True
    )
    interpretation = relationship("Interpretation", back_populates="audio_recordings")
    prediction = relationship("ModelPrediction", back_populates="audio_recordings")


class AudioFeature(Base):
    """
    Extracted acoustic features from audio recordings.
    
    Stores the 150+ acoustic features extracted from speech recordings including:
    - Prosodic features: timing, rhythm, energy patterns
    - Voice quality: jitter, shimmer, HNR
    - Spectral features: MFCCs, formants, spectral characteristics
    - Complexity measures: fractal dimensions, entropy
    
    Features are validated to exclude NaN and infinite values before storage.
    """
    __tablename__ = "audio_features"

    feature_id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(
        Integer,
        ForeignKey("audio_recordings.recording_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    feature_name = Column(String(50), nullable=False, index=True)
    feature_value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    recording = relationship("AudioRecording", back_populates="features")



class Interpretation(Base):
    __tablename__ = "interpretations"

    interpretation_id = Column(Integer, primary_key=True, index=True)
    interpreter_id = Column(Integer, nullable=True)  # Could FK to users/clinicians table
    interpretation_text = Column(Text, nullable=False)
    interpretation_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    audio_recordings = relationship("AudioRecording", back_populates="interpretation")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    predicted_class = Column(String(50), nullable=False)
    prediction_probability = Column(Float, nullable=True)
    prediction_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    audio_recordings = relationship("AudioRecording", back_populates="prediction")


class AccelerometerData(Base):
    __tablename__ = "accelerometer_data"

    acc_data_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    device_type = Column(String(50), nullable=True)
    sampling_rate = Column(Float, nullable=True)
    activity_type = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="accel_sessions")
    readings = relationship("AccelerometerReading", back_populates="session")


class AccelerometerReading(Base):
    __tablename__ = "accelerometer_readings"

    reading_id = Column(Integer, primary_key=True, index=True)
    acc_data_id = Column(Integer, ForeignKey("accelerometer_data.acc_data_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    x_axis = Column(Float, nullable=False)
    y_axis = Column(Float, nullable=False)
    z_axis = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    session = relationship("AccelerometerData", back_populates="readings")


class OpenPoseData(Base):
    __tablename__ = "openpose_data"

    openpose_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    video_file_path = Column(String(255), nullable=False)
    frame_rate = Column(Float, nullable=True)
    activity_type = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="openpose_sessions")
    keypoints = relationship("OpenPoseKeypoint", back_populates="session")


class OpenPoseKeypoint(Base):
    __tablename__ = "openpose_keypoints"

    keypoint_id = Column(Integer, primary_key=True, index=True)
    openpose_id = Column(Integer, ForeignKey("openpose_data.openpose_id"), nullable=False)
    frame_number = Column(Integer, nullable=False)
    keypoint_index = Column(Integer, nullable=False)
    keypoint_name = Column(String(50), nullable=True)
    x_position = Column(Float, nullable=False)
    y_position = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    session = relationship("OpenPoseData", back_populates="keypoints")
