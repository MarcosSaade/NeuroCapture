from sqlalchemy import (
    Column, Integer, String, Float, Text,
    Date, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    study_identifier = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    demographics = relationship("Demographic", back_populates="patient")
    assessments = relationship("CognitiveAssessment", back_populates="patient")
    accel_sessions = relationship("AccelerometerData", back_populates="patient")
    openpose_sessions = relationship("OpenPoseData", back_populates="patient")


class Demographic(Base):
    __tablename__ = "demographics"

    demographic_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    education_years = Column(Integer, nullable=True)
    collection_date = Column(Date, nullable=False)
    # add ENASEM fields here...
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="demographics")


class CognitiveAssessment(Base):
    __tablename__ = "cognitive_assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessment_type = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    max_possible_score = Column(Float, nullable=True)
    diagnosis = Column(String(50), nullable=True)
    duration_total_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="assessments")
    audio_recordings = relationship("AudioRecording", back_populates="assessment")


class AudioRecording(Base):
    __tablename__ = "audio_recordings"

    recording_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("cognitive_assessments.assessment_id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    filename = Column(String(100), nullable=False)
    recording_date = Column(DateTime, nullable=False)
    recording_device = Column(String(50), nullable=True)
    task_type = Column(String(100), nullable=True)
    interpretation_id = Column(Integer, ForeignKey("interpretations.interpretation_id"), nullable=True)
    prediction_id = Column(Integer, ForeignKey("model_predictions.prediction_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    assessment = relationship("CognitiveAssessment", back_populates="audio_recordings")
    features = relationship("AudioFeature", back_populates="recording")
    interpretation = relationship("Interpretation", back_populates="audio_recordings")
    prediction = relationship("ModelPrediction", back_populates="audio_recordings")


class AudioFeature(Base):
    __tablename__ = "audio_features"

    feature_id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("audio_recordings.recording_id"), nullable=False)
    feature_name = Column(String(50), nullable=False)
    feature_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    recording = relationship("AudioRecording", back_populates="features")


class Interpretation(Base):
    __tablename__ = "interpretations"

    interpretation_id = Column(Integer, primary_key=True, index=True)
    interpreter_id = Column(Integer, nullable=True)  # Could FK to users/clinicians table
    interpretation_text = Column(Text, nullable=False)
    interpretation_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    audio_recordings = relationship("AudioRecording", back_populates="interpretation")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    predicted_class = Column(String(50), nullable=False)
    prediction_probability = Column(Float, nullable=True)
    prediction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    audio_recordings = relationship("AudioRecording", back_populates="prediction")


class AccelerometerData(Base):
    __tablename__ = "accelerometer_data"

    acc_data_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    session_date = Column(DateTime, nullable=False)
    device_type = Column(String(50), nullable=True)
    sampling_rate = Column(Float, nullable=True)
    activity_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="accel_sessions")
    readings = relationship("AccelerometerReading", back_populates="session")


class AccelerometerReading(Base):
    __tablename__ = "accelerometer_readings"

    reading_id = Column(Integer, primary_key=True, index=True)
    acc_data_id = Column(Integer, ForeignKey("accelerometer_data.acc_data_id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    x_axis = Column(Float, nullable=False)
    y_axis = Column(Float, nullable=False)
    z_axis = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    session = relationship("AccelerometerData", back_populates="readings")


class OpenPoseData(Base):
    __tablename__ = "openpose_data"

    openpose_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    session_date = Column(DateTime, nullable=False)
    video_file_path = Column(String(255), nullable=False)
    frame_rate = Column(Float, nullable=True)
    activity_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

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
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    session = relationship("OpenPoseData", back_populates="keypoints")
