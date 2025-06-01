# app/db/models/vote.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
import uuid
from .project import Base

class Vote(Base):
    __tablename__ = "votes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"))
    tag_id = Column(String, ForeignKey("tags.id"))
    user_id = Column(String, ForeignKey("users.id"))
    voted_at = Column(DateTime, default=datetime.utcnow)
