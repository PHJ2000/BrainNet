# backend/app/models/tag_summary.py
from pydantic import BaseModel
from datetime import datetime

class TagSummaryOut(BaseModel):
    id: int
    tag_id: int
    summary_text: str
    created_at: datetime

    class Config:
        from_attributes = True
