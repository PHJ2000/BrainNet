from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain, hashed) -> bool:
    return pwd_context.verify(plain, hashed)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: schemas.UserCreate):
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        name=user_in.name
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

# 이하 프로젝트, 노드, 태그, 투표, 히스토리 CRUD 함수 구현
