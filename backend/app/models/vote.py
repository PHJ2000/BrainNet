from pydantic import BaseModel
from typing import Optional

class VoteOut(BaseModel):
    id: str
    project_id: str
    tag_id: str
    user_id: str
    voted_at: str

class HistoryOut(BaseModel):
    id: str
    project_id: str
    tag_id: str
    summary: str
    decided_at: str
    decided_by: str
