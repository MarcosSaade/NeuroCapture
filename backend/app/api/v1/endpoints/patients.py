# patients.py

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
)
async def create_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_in: PatientCreate
) -> Patient:
    return await crud_create_patient(db=db, obj_in=patient_in)


@router.get(
    "/{patient_id}",
    response_model=Patient,
)
async def read_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_id: int
) -> Patient:
    patient = await crud_get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get(
    "/",
    response_model=List[Patient],
)
async def read_patients(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[Patient]:
    return await crud_get_patients(db=db, skip=skip, limit=limit)


@router.put(
    "/{patient_id}",
    response_model=Patient,
)
async def update_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_id: int,
    patient_in: PatientUpdate
) -> Patient:
    db_obj = await crud_get_patient(db=db, patient_id=patient_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Patient not found")
    return await crud_update_patient(db=db, db_obj=db_obj, obj_in=patient_in)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_id: int
) -> None:
    await crud_delete_patient(db=db, patient_id=patient_id)
    return None
