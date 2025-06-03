# app/db/models/tag.py
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.base import Base

class Tag(Base):
    __tablename__ = "tag"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(80), nullable=False)
    color = Column(String(7), nullable=True)

    project = relationship("Project", backref="tags", foreign_keys=[project_id])
