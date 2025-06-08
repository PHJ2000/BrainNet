# backend/app/models/node.py
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class NodeCreate(BaseModel):
    content: Optional[str] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    depth: Optional[int] = 0
    order: Optional[int] = 0
    ai_prompt: Optional[str] = None
    parent_id: Optional[int] = None
    state: Optional[str] = None  # ← 기본값은 ACTIVE, 입력 가능

class NodeUpdate(BaseModel):
    content: Optional[str] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    depth: Optional[int] = None
    order: Optional[int] = None

class NodeOut(BaseModel):
    id: int
    project_id: int
    author_id: Optional[int]
    content: str
    state: str
    pos_x: Optional[float]
    pos_y: Optional[float]
    depth: int
    order_index: int
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[int] =[]


    class Config:
        from_attributes = True
