# app/db/models/history.py
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from datetime import datetime
from app.db.models.base import Base
class ProjectHistory(Base):
    __tablename__ = "project_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    tag_summary_id = Column(BigInteger, ForeignKey("tag_summary.id"), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
