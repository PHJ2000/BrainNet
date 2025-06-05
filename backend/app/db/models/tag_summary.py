# app/db/models/tag_summary.py
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from datetime import datetime
from app.db.models.base import Base

class TagSummary(Base):
    __tablename__ = "tag_summary"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tag_id = Column(BigInteger, ForeignKey("tag.id", ondelete="CASCADE"), nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
