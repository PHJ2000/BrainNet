# app/db/models/vote.py
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.db.models.base import Base

class Vote(Base):
    __tablename__ = "vote"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tag_summary_id = Column(BigInteger, ForeignKey("tag_summary.id", ondelete="CASCADE"), nullable=False)
    voter_id = Column(BigInteger, ForeignKey("app_user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tag_summary_id", "voter_id"),
    )
