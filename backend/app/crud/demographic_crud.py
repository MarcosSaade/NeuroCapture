from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models import Demographic as DemographicModel
from app.schemas.demographic_schema import DemographicCreate, DemographicUpdate
from fastapi import HTTPException

async def get_demographics(db: AsyncSession, patient_id: int):
    result = await db.execute(select(DemographicModel).where(DemographicModel.patient_id == patient_id))
    return result.scalars().all()

async def get_demographic(db: AsyncSession, demographic_id: int):
    result = await db.execute(select(DemographicModel).where(DemographicModel.demographic_id == demographic_id))
    return result.scalars().first()

async def create_demographic(db: AsyncSession, patient_id: int, obj_in: DemographicCreate):
    db_obj = DemographicModel(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_demographic(db: AsyncSession, db_obj: DemographicModel, obj_in: DemographicUpdate):
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(db_obj, field, val)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_demographic(db: AsyncSession, demographic_id: int):
    obj = await get_demographic(db, demographic_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Demographic not found")
    await db.delete(obj)
    await db.commit()
