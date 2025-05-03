from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models import Patient

router = APIRouter()

@router.get("/ping-db")
async def ping_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    return {"count": len(patients), "sample": [p.study_identifier for p in patients[:3]]}
