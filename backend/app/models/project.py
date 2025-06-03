# backend/app/models/project.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str = Field(..., example="새 프로젝트")
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None
    member_count: Optional[int] = None
    node_count: Optional[int] = None
    tag_count: Optional[int] = None

    class Config:
        from_attributes = True
