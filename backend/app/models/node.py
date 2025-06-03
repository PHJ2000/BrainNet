# backend/app/models/node.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NodeCreate(BaseModel):
    content: Optional[str] = None
    parent_id: Optional[int] = None
    depth: Optional[int] = 0
    order_index: Optional[int] = 0
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    ai_prompt: Optional[str] = None

class NodeUpdate(BaseModel):
    content: Optional[str] = None
    depth: Optional[int] = None
    order_index: Optional[int] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None

class NodeOut(BaseModel):
    id: int
    project_id: int
    parent_id: Optional[int]
    author_id: Optional[int]
    content: str
    state: str
    depth: int
    order_index: int
    pos_x: Optional[float]
    pos_y: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
