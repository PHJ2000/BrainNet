from sqlalchemy import Column, BigInteger, DateTime, Enum, JSON, ForeignKey
from datetime import datetime
from app.db.models.base import Base
import enum

class ActType(enum.Enum):
    NODE_CREATE = "NODE_CREATE"
    NODE_UPDATE = "NODE_UPDATE"
    NODE_DELETE = "NODE_DELETE"
    TAG_APPLY = "TAG_APPLY"
    VOTE_CAST = "VOTE_CAST"
    INVITE_SENT = "INVITE_SENT"
    INVITE_ACCEPT = "INVITE_ACCEPT"

class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("app_user.id"), nullable=True)
    project_id = Column(BigInteger, ForeignKey("project.id"), nullable=True)
    type = Column(Enum(ActType, name="act_type_t"), nullable=False)
    payload = Column(JSON, nullable=True)
    logged_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
