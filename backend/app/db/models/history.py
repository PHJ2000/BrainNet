# app/db/models/history.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from datetime import datetime
import uuid
from .project import Base

class History(Base):
    __tablename__ = "history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"))
    tag_id = Column(String, ForeignKey("tags.id"))
    summary = Column(Text)
    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String, ForeignKey("users.id"))
