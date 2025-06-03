# app/db/models/node_metrics.py
from sqlalchemy import Column, BigInteger, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from app.db.models.base import Base

class NodeMetrics(Base):
    __tablename__ = "node_metrics"

    node_id = Column(BigInteger, ForeignKey("node.id", ondelete="CASCADE"), primary_key=True)
    subtree_size = Column(Integer, nullable=False)
    density_score = Column(Float, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
