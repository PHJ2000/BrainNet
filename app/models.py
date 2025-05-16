import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, Float, Enum, Table, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base

# Node-Tag M:N 관계 테이블
node_tag = Table(
    'node_tag', Base.metadata,
    Column('node_id', String, ForeignKey('nodes.id'), primary_key=True),
    Column('tag_id', String, ForeignKey('tags.id'), primary_key=True),
)

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User")

class Node(Base):
    __tablename__ = 'nodes'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    status = Column(Enum("ACTIVE", "GHOST", name="node_status"), default="ACTIVE")
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    depth = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    tags = relationship("Tag", secondary=node_tag, back_populates="nodes")

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    nodes = relationship("Node", secondary=node_tag, back_populates="tags")

class ProjectHistoryEntry(Base):
    __tablename__ = 'project_history'
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    tag_id = Column(String, ForeignKey('tags.id'), nullable=False)
    summary = Column(Text, nullable=False)
    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String, ForeignKey('users.id'), nullable=False)

# 투표, 초대 모델은 내부 로직에서만 사용하므로 별도 DB 테이블 생략 가능
