from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db
from app.schemas.demographic_schema import Demographic, DemographicCreate, DemographicUpdate
from app.crud.demographic_crud import (
    get_demographics, get_demographic,
    create_demographic, update_demographic, delete_demographic
)

router = APIRouter(prefix="/patients/{patient_id}/demographics", tags=["demographics"])

@router.get("/", response_model=List[Demographic])
async def list_demographics(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await get_demographics(db, patient_id)

@router.post("/", response_model=Demographic, status_code=status.HTTP_201_CREATED)
async def create_demo(patient_id: int, demo_in: DemographicCreate, db: AsyncSession = Depends(get_db)):
    return await create_demographic(db, patient_id, demo_in)

@router.get("/{demographic_id}", response_model=Demographic)
async def read_demo(patient_id: int, demographic_id: int, db: AsyncSession = Depends(get_db)):
    obj = await get_demographic(db, demographic_id)
    if not obj or obj.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{demographic_id}", response_model=Demographic)
async def update_demo(patient_id: int, demographic_id: int, demo_in: DemographicUpdate, db: AsyncSession = Depends(get_db)):
    obj = await get_demographic(db, demographic_id)
    if not obj or obj.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Not found")
    return await update_demographic(db, obj, demo_in)

@router.delete("/{demographic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_demo(patient_id: int, demographic_id: int, db: AsyncSession = Depends(get_db)):
    await delete_demographic(db, demographic_id)
    return None
