# app/db/models/__init__.py
from .user import User
from .project import Project
from .node import Node
from .tag import Tag
from .vote import Vote
from .history import History
from .base import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
