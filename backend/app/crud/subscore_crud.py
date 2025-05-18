from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models import AssessmentSubscore
from app.schemas.subscore_schema import SubscoreCreate, SubscoreUpdate

async def get_subscores(db: AsyncSession, assessment_id: int):
    result = await db.execute(
        select(AssessmentSubscore).where(
            AssessmentSubscore.assessment_id == assessment_id
        )
    )
    return result.scalars().all()

async def create_subscore(
    db: AsyncSession, assessment_id: int, obj_in: SubscoreCreate
):
    db_obj = AssessmentSubscore(
        assessment_id=assessment_id, **obj_in.model_dump()
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_subscore(
    db: AsyncSession, db_obj: AssessmentSubscore, obj_in: SubscoreUpdate
):
    data = obj_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(db_obj, field, val)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_subscore(db: AsyncSession, subscore_id: int):
    obj = await db.get(AssessmentSubscore, subscore_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Subscore not found")
    await db.delete(obj)
    await db.commit()
