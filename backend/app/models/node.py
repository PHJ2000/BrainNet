# backend/app/models/node.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NodeCreate(BaseModel):
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    depth: Optional[int] = 0
    order: Optional[int] = 0
    ai_prompt: Optional[str] = None
    parent_id: Optional[int] = None

class NodeUpdate(BaseModel):
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    depth: Optional[int] = None
    order: Optional[int] = None

class NodeOut(BaseModel):
    id: int
    project_id: int
    authors: Optional[int]
    content: str
    status: str
    x: Optional[float]
    y: Optional[float]
    depth: int
    order: int
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
