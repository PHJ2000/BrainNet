# app/db/models/user.py
from sqlalchemy import Column, BigInteger, String, DateTime
from datetime import datetime
from app.db.models.base import Base

class User(Base):
    __tablename__ = "app_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=True)
    email = Column(String(120), unique=True, nullable=False)
    pw_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
