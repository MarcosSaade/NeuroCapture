from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException
from app.models import Patient as PatientModel
from app.schemas.patient_schema import PatientCreate, PatientUpdate

async def create_patient(db: AsyncSession, *, obj_in: PatientCreate) -> PatientModel:
    db_obj = PatientModel(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_patient(db: AsyncSession, *, patient_id: int) -> PatientModel | None:
    result = await db.execute(select(PatientModel).where(PatientModel.patient_id == patient_id))
    return result.scalars().first()

async def get_patients(db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[PatientModel]:
    result = await db.execute(select(PatientModel).offset(skip).limit(limit))
    return result.scalars().all()

async def update_patient(
    db: AsyncSession,
    *,
    db_obj: PatientModel,
    obj_in: PatientUpdate
) -> PatientModel:
    obj_data = db_obj.__dict__
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_patient(db: AsyncSession, *, patient_id: int) -> None:
    result = await db.execute(select(PatientModel).where(PatientModel.patient_id == patient_id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Patient not found")
    await db.delete(db_obj)
    await db.commit()
