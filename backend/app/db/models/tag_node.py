# app/db/models/tag_node.py
from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from app.db.models.base import Base

class TagNode(Base):
    __tablename__ = "tag_node"

    tag_id = Column(BigInteger, ForeignKey("tag.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(BigInteger, ForeignKey("node.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("tag_id", "node_id"),
    )
