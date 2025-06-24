"""
Patient Management API Endpoints

RESTful API endpoints for managing patient records in the NeuroCapture system.
Provides CRUD operations for patient entities with study identifier validation.

Features:
- Create patients with unique study identifiers
- Retrieve individual patients or paginated lists
- Update patient information (study identifier only)
- Delete patients with cascade data removal
- Input validation and error handling

Author: NeuroCapture Development Team
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.patient_schema import Patient, PatientCreate, PatientUpdate
from app.crud.patient_crud import (
    create_patient as crud_create_patient,
    get_patient as crud_get_patient,
    get_patients as crud_get_patients,
    update_patient as crud_update_patient,
    delete_patient as crud_delete_patient,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "/",
    response_model=Patient,
    status_code=status.HTTP_201_CREATED,
    summary="Create new patient",
    description="Create a new patient record with unique study identifier"
)
async def create_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_in: PatientCreate
) -> Patient:
    """
    Create a new patient record.
    
    Args:
        patient_in: Patient creation data with study_identifier
        
    Returns:
        Created patient record with assigned patient_id
        
    Raises:
        HTTPException: 400 if study_identifier already exists
    """
    return await crud_create_patient(db=db, obj_in=patient_in)


@router.get(
    "/{patient_id}",
    response_model=Patient,
    summary="Get patient by ID",
    description="Retrieve a specific patient record by patient_id"
)
async def read_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_id: int
) -> Patient:
    """
    Retrieve a patient by ID.
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        Patient record with all basic information
        
    Raises:
        HTTPException: 404 if patient not found
    """
    patient = await crud_get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Patient not found"
        )
    return patient


@router.get(
    "/",
    response_model=List[Patient],
    summary="List all patients",
    description="Retrieve paginated list of all patients in the system"
)
async def read_patients(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[Patient]:
    """
    List patients with pagination.
    
    Args:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        
    Returns:
        List of patient records
    """
    return await crud_get_patients(db=db, skip=skip, limit=limit)


@router.put(
    "/{patient_id}",
    response_model=Patient,
    summary="Update patient",
    description="Update patient information (currently study identifier only)"
)
async def update_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_id: int,
    patient_in: PatientUpdate
) -> Patient:
    """
    Update patient information.
    
    Args:
        patient_id: Patient to update
        patient_in: Updated patient data
        
    Returns:
        Updated patient record
        
    Raises:
        HTTPException: 404 if patient not found
        HTTPException: 400 if study_identifier conflicts
    """
    db_obj = await crud_get_patient(db=db, patient_id=patient_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Patient not found"
        )
    return await crud_update_patient(db=db, db_obj=db_obj, obj_in=patient_in)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete patient",
    description="Delete patient and all associated data (demographics, assessments, recordings)"
)
async def delete_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_id: int
) -> None:
    """
    Delete a patient and all associated data.
    
    Args:
        patient_id: Patient to delete
        
    Note:
        This operation cascades to delete all related data including:
        - Demographics
        - Cognitive assessments and subscores
        - Audio recordings and features
        
    Raises:
        HTTPException: 404 if patient not found
    """
    await crud_delete_patient(db=db, patient_id=patient_id)
    return None
