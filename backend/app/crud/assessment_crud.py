from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException
from app.models import CognitiveAssessment as AssessmentModel
from app.schemas.assessment_schema import AssessmentCreate, AssessmentUpdate

async def get_assessments(db: AsyncSession, patient_id: int) -> list[AssessmentModel]:
    result = await db.execute(
        select(AssessmentModel)
        .where(AssessmentModel.patient_id == patient_id)
        .order_by(AssessmentModel.assessment_date.desc())
    )
    return result.scalars().all()

async def get_assessment(db: AsyncSession, assessment_id: int) -> AssessmentModel | None:
    result = await db.execute(
        select(AssessmentModel)
        .where(AssessmentModel.assessment_id == assessment_id)
    )
    return result.scalars().first()

async def create_assessment(
    db: AsyncSession, patient_id: int, obj_in: AssessmentCreate
) -> AssessmentModel:
    db_obj = AssessmentModel(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_assessment(
    db: AsyncSession, db_obj: AssessmentModel, obj_in: AssessmentUpdate
) -> AssessmentModel:
    data = obj_in.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(db_obj, field, val)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_assessment(db: AsyncSession, assessment_id: int) -> None:
    obj = await get_assessment(db, assessment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(obj)
    await db.commit()
