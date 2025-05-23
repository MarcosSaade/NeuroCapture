from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from fastapi import HTTPException

from app.models import CognitiveAssessment as AssessmentModel, AssessmentSubscore
from app.schemas.assessment_schema import AssessmentCreate, AssessmentUpdate
from app.schemas.subscore_schema import SubscoreCreate

async def get_assessments(db: AsyncSession, patient_id: int) -> list[AssessmentModel]:
    result = await db.execute(
        select(AssessmentModel)
        .where(AssessmentModel.patient_id == patient_id)
        .options(
            selectinload(AssessmentModel.subscores) 
        )
        .order_by(AssessmentModel.assessment_date.desc())
    )
    return result.scalars().all()

async def get_assessment(db: AsyncSession, assessment_id: int) -> AssessmentModel | None:
    result = await db.execute(
        select(AssessmentModel)
        .where(AssessmentModel.assessment_id == assessment_id)
        .options(
            selectinload(AssessmentModel.subscores)
        )
    )
    return result.scalars().first()

async def create_assessment(
    db: AsyncSession, patient_id: int, obj_in: AssessmentCreate
) -> AssessmentModel:
    # First, insert the assessment itself
    db_obj = AssessmentModel(
        patient_id=patient_id,
        **obj_in.model_dump(exclude={'subscores'})  # don’t pass subscores here
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)

    # Then insert any subscores (if present)
    for sub in obj_in.subscores or []:
        current_sub_db = AssessmentSubscore(assessment_id=db_obj.assessment_id, **sub.model_dump())
        db.add(current_sub_db)
    if obj_in.subscores:
        await db.commit()

    # Finally re-query with subscores eagerly loaded
    result = await db.execute(
        select(AssessmentModel)
        .where(AssessmentModel.assessment_id == db_obj.assessment_id)
        .options(selectinload(AssessmentModel.subscores))
    )
    return result.scalars().one()

async def update_assessment(
    db: AsyncSession, db_obj: AssessmentModel, obj_in: AssessmentUpdate
) -> AssessmentModel:
    data = obj_in.model_dump(exclude_unset=True, exclude={'subscores'})
    for field, val in data.items():
        setattr(db_obj, field, val)
    db.add(db_obj)
    await db.commit()

    # If the caller provided a new subscores list, wipe & re-insert:
    if obj_in.subscores is not None:
        # delete existing
        await db.execute(
            delete(AssessmentSubscore)
            .where(AssessmentSubscore.assessment_id == db_obj.assessment_id)
        )
        # insert new
        for sub in obj_in.subscores:
            db.add(AssessmentSubscore(
                assessment_id=db_obj.assessment_id,
                **sub.model_dump()
            ))
        await db.commit()

    # Re-fetch with subscores
    await db.refresh(db_obj)  # Refresh the main object to sync with DB
    result = await db.execute(
        select(AssessmentModel)
        .where(AssessmentModel.assessment_id == db_obj.assessment_id)
        .options(selectinload(AssessmentModel.subscores))
    )
    return result.scalars().one()

async def delete_assessment(db: AsyncSession, assessment_id: int) -> None:
    obj = await get_assessment(db, assessment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(obj)
    await db.commit()
