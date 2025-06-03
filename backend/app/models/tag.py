# backend/app/models/tag.py
from pydantic import BaseModel
from typing import Optional, List

class TagCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    node_id : str

class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class TagOut(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    node_count: int
    summary: str
    nodes: List[str] | None = None
