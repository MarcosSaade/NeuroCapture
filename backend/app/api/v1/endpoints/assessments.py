# backend/app/api/v1/endpoints/assessments.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.crud.assessment_crud import (
    get_assessments,
    get_assessment,
    create_assessment as crud_create_assessment,
    update_assessment as crud_update_assessment,
    delete_assessment as crud_delete_assessment,
)
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentInDB,
)

router = APIRouter(
    prefix="/patients/{patient_id}/assessments",
    tags=["assessments"],
)


@router.get("/", response_model=List[AssessmentInDB])
async def list_assessments(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_assessments(db, patient_id)


@router.post(
    "/",
    response_model=AssessmentInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment_endpoint(
    patient_id: int,
    assessment_in: AssessmentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud_create_assessment(db, patient_id, assessment_in)


@router.get("/{assessment_id}", response_model=AssessmentInDB)
async def read_assessment(
    patient_id: int,
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
):
    obj = await get_assessment(db, assessment_id)
    if not obj or obj.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.put("/{assessment_id}", response_model=AssessmentInDB)
async def update_assessment_endpoint(
    patient_id: int,
    assessment_id: int,
    assessment_in: AssessmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await get_assessment(db, assessment_id)
    if not obj or obj.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Not found")
    return await crud_update_assessment(db, obj, assessment_in)


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment_endpoint(
    patient_id: int,
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
):
    await crud_delete_assessment(db, assessment_id)
    return None
