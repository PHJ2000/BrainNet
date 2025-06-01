# backend/app/models/project.py
from pydantic import BaseModel, Field
from typing import Optional

class ProjectCreate(BaseModel):
    name: str = Field(..., example="새 프로젝트")
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: str
    updated_at: str
    member_count: int | None = None
    node_count: int | None = None
    tag_count:  int | None = None
