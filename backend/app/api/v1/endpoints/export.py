from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import csv
import io

from app.api.dependencies import get_db
from app.models import Patient, CognitiveAssessment, AudioRecording, AudioFeature

router = APIRouter(
    prefix="/export",
    tags=["export"],
)

@router.get("/features/csv")
async def export_all_features_csv(
    db: AsyncSession = Depends(get_db),
):
    """
    Export all extracted audio features for all patients/assessments/recordings as CSV.
    """
    try:
        # Query all features with their related data
        result = await db.execute(
            select(AudioFeature)
            .options(
                selectinload(AudioFeature.recording)
                .selectinload(AudioRecording.assessment)
                .selectinload(CognitiveAssessment.patient)
            )
            .order_by(
                AudioFeature.recording_id,
                AudioFeature.feature_name
            )
        )
        features = result.scalars().all()
        
        if not features:
            raise HTTPException(
                status_code=404, 
                detail="No features found for export"
            )
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = [
            'Patient ID',
            'Study Identifier', 
            'Assessment ID',
            'Assessment Type',
            'Assessment Date',
            'Recording ID',
            'Recording Filename',
            'Task Type',
            'Recording Device',
            'Recording Date',
            'Feature Name',
            'Feature Value',
            'Feature Created At'
        ]
        writer.writerow(headers)
        
        # Write data rows
        for feature in features:
            recording = feature.recording
            assessment = recording.assessment
            patient = assessment.patient
            
            row = [
                patient.patient_id,
                patient.study_identifier or '',
                assessment.assessment_id,
                assessment.assessment_type or '',
                assessment.assessment_date.isoformat() if assessment.assessment_date else '',
                recording.recording_id,
                recording.filename or '',
                recording.task_type or '',
                recording.recording_device or '',
                recording.recording_date.isoformat() if recording.recording_date else '',
                feature.feature_name,
                feature.feature_value,
                feature.created_at.isoformat() if feature.created_at else ''
            ]
            writer.writerow(row)
        
        # Prepare file for download
        output.seek(0)
        
        def generate():
            yield output.getvalue()
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=neurocapture_features_export.csv"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export features: {e}"
        )
