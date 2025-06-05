# backend/app/models/node_version.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NodeVersionOut(BaseModel):
    id: int
    node_id: int
    version_no: int
    content: str
    author_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
