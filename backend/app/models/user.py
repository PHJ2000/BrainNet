# backend/app/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr

class UserRead(UserBase):
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class UserSimple(UserBase):
    id: int

    class Config:
        from_attributes = True
