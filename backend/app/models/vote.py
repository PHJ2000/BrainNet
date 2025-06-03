# backend/app/models/vote.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VoteOut(BaseModel):
    id: int
    tag_summary_id: int
    voter_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

class HistoryOut(BaseModel):
    id: int
    project_id: int
    tag_summary_id: Optional[int]
    decided_at: datetime

    class Config:
        orm_mode = True
