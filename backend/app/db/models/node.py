# app/db/models/node.py
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
from .project import Base
from app.db.models.base import Base
class NodeStatusEnum(str):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"))
    content = Column(String)
    x = Column(Float)
    y = Column(Float)
    depth = Column(Integer, default=0)
    order = Column(Integer, default=0)
    status = Column(String, default="inactive")
    ai_prompt = Column(String)
    parent_id = Column(String)

    project = relationship("Project", backref="nodes")
