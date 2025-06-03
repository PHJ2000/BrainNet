# backend/app/models/history.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectHistoryOut(BaseModel):
    id: int
    project_id: int
    tag_summary_id: Optional[int]
    decided_at: datetime

    class Config:
        from_attributes = True
