from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException

from app.models import (
    CognitiveAssessment as AssessmentModel,
    AssessmentSubscore as SubscoreModel,
)
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentUpdate,
    SubscoreCreate,
)


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


async def get_subscores(db: AsyncSession, assessment_id: int) -> list[SubscoreModel]:
    result = await db.execute(
        select(SubscoreModel)
        .where(SubscoreModel.assessment_id == assessment_id)
    )
    return result.scalars().all()


async def create_assessment(
    db: AsyncSession,
    patient_id: int,
    obj_in: AssessmentCreate
) -> AssessmentModel:
    data = obj_in.model_dump()
    subs = data.pop("subscores", None) or []
    db_obj = AssessmentModel(patient_id=patient_id, **data)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)

    # create nested subscores
    for s in subs:
        sub_obj = SubscoreModel(assessment_id=db_obj.assessment_id, **s)
        db.add(sub_obj)
    if subs:
        await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_assessment(
    db: AsyncSession,
    db_obj: AssessmentModel,
    obj_in: AssessmentUpdate
) -> AssessmentModel:
    data = obj_in.model_dump(exclude_unset=True)
    subs = data.pop("subscores", None)

    # update assessment fields
    for field, val in data.items():
        setattr(db_obj, field, val)
    db.add(db_obj)
    await db.commit()

    # replace subscores if provided
    if subs is not None:
        # delete existing
        await db.execute(
            delete(SubscoreModel)
            .where(SubscoreModel.assessment_id == db_obj.assessment_id)
        )
        # create new
        for s in subs:
            sub_obj = SubscoreModel(assessment_id=db_obj.assessment_id, **s)
            db.add(sub_obj)
        await db.commit()

    await db.refresh(db_obj)
    return db_obj


async def delete_assessment(db: AsyncSession, assessment_id: int) -> None:
    obj = await get_assessment(db, assessment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(obj)
    await db.commit()
