# #backend/app/models/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True