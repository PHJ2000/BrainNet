# backend/app/models/activity_log.py
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ActivityLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    project_id: Optional[int]
    type: str
    payload: Optional[Any]
    logged_at: datetime

    class Config:
        orm_mode = True
