from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class UserRead(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str]
    created_at: str
