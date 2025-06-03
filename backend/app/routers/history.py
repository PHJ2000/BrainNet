# backend/app/routers/history.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.vote import HistoryOut   # Pydantic 스키마
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m
from app.db.models.history import ProjectHistory
from app.db.session import AsyncSessionLocal

router = APIRouter(prefix="/projects/{project_id}/history", tags=["History"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("", response_model=List[HistoryOut])
async def list_history(
    project_id: int,
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    _m(uid, project_id)
    result = await db.execute(
        select(ProjectHistory).where(ProjectHistory.project_id == project_id)
    )
    entries = result.scalars().all()
    return entries

@router.get("/{entry_id}", response_model=HistoryOut)
async def get_history(
    project_id: int,
    entry_id: int,
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    _m(uid, project_id)
    result = await db.execute(
        select(ProjectHistory).where(
            ProjectHistory.id == entry_id,
            ProjectHistory.project_id == project_id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(404, "History entry not found")
    return entry
