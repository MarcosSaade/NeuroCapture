from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models import AssessmentSubscore
from app.schemas.subscore_schema import SubscoreCreate, SubscoreRead, SubscoreUpdate
from app.crud.subscore_crud import (
    get_subscores,
    create_subscore,
    update_subscore,
    delete_subscore
)

router = APIRouter(
    prefix="/patients/{patient_id}/assessments/{assessment_id}/subscores",
    tags=["subscores"],
)

@router.get("/", response_model=List[SubscoreRead])
async def list_subscores(
    patient_id: int,
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_subscores(db, assessment_id)

@router.post(
    "/",
    response_model=SubscoreRead,
    status_code=status.HTTP_201_CREATED
)
async def create_subscore_endpoint(
    patient_id: int,
    assessment_id: int,
    subscore_in: SubscoreCreate,
    db: AsyncSession = Depends(get_db),
):
    # (Optionally verify assessment belongs to patient here)
    return await create_subscore(db, assessment_id, subscore_in)

@router.put("/{subscore_id}", response_model=SubscoreRead)
async def update_subscore_endpoint(
    patient_id: int,
    assessment_id: int,
    subscore_id: int,
    subscore_in: SubscoreUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await db.get(AssessmentSubscore, subscore_id)
    if not db_obj or db_obj.assessment_id != assessment_id:
        raise HTTPException(status_code=404, detail="Subscore not found")
    return await update_subscore(db, db_obj, subscore_in)

@router.delete(
    "/{subscore_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_subscore_endpoint(
    patient_id: int,
    assessment_id: int,
    subscore_id: int,
    db: AsyncSession = Depends(get_db),
):
    # (Optionally verify assessment_id)
    await delete_subscore(db, subscore_id)
    return None
