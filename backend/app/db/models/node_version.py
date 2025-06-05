# app/db/models/node_version.py
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.db.models.base import Base

class NodeVersion(Base):
    __tablename__ = "node_version"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey("node.id", ondelete="CASCADE"), nullable=False)
    version_no = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(BigInteger, ForeignKey("app_user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("node_id", "version_no"),
    )
