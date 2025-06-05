# backend/app/models/project_user_role.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectUserRoleOut(BaseModel):
    project_id: int
    user_id: int
    role: str
    invited_at: datetime
    accepted_at: Optional[datetime]

    class Config:
        from_attributes = True
