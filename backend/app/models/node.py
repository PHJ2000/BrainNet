# backend/app/models/node.py
from pydantic import BaseModel
from typing import Optional, List

class NodeCreate(BaseModel):
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    depth: Optional[int] = 0
    order: Optional[int] = 0
    ai_prompt: Optional[str] = None
    parent_id: Optional[str] = None

class NodeUpdate(BaseModel):
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    depth: Optional[int] = None
    order: Optional[int] = None

class NodeOut(BaseModel):
    id: str
    project_id: str
    content: str
    status: str
    x: float
    y: float
    depth: int
    order: int
    tags: List[str] = []
    parent_id: Optional[str] =None
