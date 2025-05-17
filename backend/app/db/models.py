from __future__ import annotations

"""SQLAlchemy async ORM models matching the PostgreSQL DDL spec.
This file lives at backend/app/db/models.py
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()

# ---------------------------------------------------------------------------
# ENUM types ----------------------------------------------------------------
# ---------------------------------------------------------------------------

class RoleEnum(str, PyEnum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"


class NodeStateEnum(str, PyEnum):
    GHOST = "GHOST"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ActTypeEnum(str, PyEnum):
    NODE_CREATE = "NODE_CREATE"
    NODE_UPDATE = "NODE_UPDATE"
    NODE_DELETE = "NODE_DELETE"
    TAG_APPLY = "TAG_APPLY"
    VOTE_CAST = "VOTE_CAST"
    INVITE_SENT = "INVITE_SENT"
    INVITE_ACCEPT = "INVITE_ACCEPT"

# ---------------------------------------------------------------------------
# 1. USERS -------------------------------------------------------------------
# ---------------------------------------------------------------------------

class AppUser(Base):
    __tablename__ = "app_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

# ---------------------------------------------------------------------------
# 2. PROJECTS & ROLE ---------------------------------------------------------
# ---------------------------------------------------------------------------

class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("app_user.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ProjectUserRole(Base):
    __tablename__ = "project_user_role"

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[RoleEnum] = mapped_column(SQLEnum(RoleEnum, name="role_t"), nullable=False)
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

# ---------------------------------------------------------------------------
# 3. NODES & VERSIONS --------------------------------------------------------
# ---------------------------------------------------------------------------

class Node(Base):
    __tablename__ = "node"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("node.id", ondelete="SET NULL"))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[NodeStateEnum] = mapped_column(SQLEnum(NodeStateEnum, name="node_state_t"), default=NodeStateEnum.GHOST)
    depth: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    pos_x: Mapped[float | None] = mapped_column(Float)
    pos_y: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class NodeVersion(Base):
    __tablename__ = "node_version"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("node.id", ondelete="CASCADE"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("node_id", "version_no"),)

# ---------------------------------------------------------------------------
# 4. TAGS --------------------------------------------------------------------
# ---------------------------------------------------------------------------

class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7))


class TagNode(Base):
    __tablename__ = "tag_node"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("node.id", ondelete="CASCADE"), primary_key=True)


class TagSummary(Base):
    __tablename__ = "tag_summary"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"))
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# ---------------------------------------------------------------------------
# 5. VOTING & HISTORY --------------------------------------------------------
# ---------------------------------------------------------------------------

class Vote(Base):
    __tablename__ = "vote"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_summary_id: Mapped[int] = mapped_column(ForeignKey("tag_summary.id", ondelete="CASCADE"))
    voter_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("tag_summary_id", "voter_id"),)


class ProjectHistory(Base):
    __tablename__ = "project_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    tag_summary_id: Mapped[int | None] = mapped_column(ForeignKey("tag_summary.id"))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# ---------------------------------------------------------------------------
# 6. NODE METRICS -----------------------------------------------------------
# ---------------------------------------------------------------------------

class NodeMetrics(Base):
    __tablename__ = "node_metrics"

    node_id: Mapped[int] = mapped_column(ForeignKey("node.id", ondelete="CASCADE"), primary_key=True)
    subtree_size: Mapped[int] = mapped_column(Integer, default=1)
    density_score: Mapped[float] = mapped_column(Float, default=1.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# ---------------------------------------------------------------------------
# 7. ACTIVITY LOG & INVITE TOKEN -------------------------------------------
# ---------------------------------------------------------------------------

class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("project.id"))
    type: Mapped[ActTypeEnum] = mapped_column(SQLEnum(ActTypeEnum, name="act_type_t"))
    payload: Mapped[dict | None] = mapped_column(JSON)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class InviteToken(Base):
    __tablename__ = "invite_token"

    token: Mapped[str] = mapped_column(String(48), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SQLEnum(RoleEnum, name="role_t"), default=RoleEnum.EDITOR)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("email", "project_id", name="idx_invite_email_project"),
    )
