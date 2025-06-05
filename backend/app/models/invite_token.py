# backend/app/models/invite_token.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InviteTokenOut(BaseModel):
    token: str
    project_id: int
    email: str
    role: str
    expires_at: datetime
    accepted_at: Optional[datetime]

    class Config:
        from_attributes = True
