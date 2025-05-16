from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str]

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes=True

class TagSummary(BaseModel):
    project_id: str
    tag_id: str
    tag_name: str
    summary: str
    nodes_contributed: int

class Project(BaseModel):
    id: str
    name: str
    owner_id: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True

class Node(BaseModel):
    id: str
    content: str
    status: str
    x: float
    y: float
    depth: int
    order: int
    tags: List[str]

    class Config:
        from_attributes=True

class Tag(BaseModel):
    id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    node_count: Optional[int]
    summary: Optional[str]

    class Config:
        from_attributes=True

class ProjectHistoryEntry(BaseModel):
    id: int
    project_id: str
    tag_id: str
    summary: str
    decided_at: datetime
    decided_by: str

    class Config:
        from_attributes=True
