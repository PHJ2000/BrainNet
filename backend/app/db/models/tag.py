# app/db/models/tag.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from .project import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    color = Column(String)
    summary = Column(Text)

    project = relationship("Project", backref="tags")
