# backend/app/routers/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.auth import UserCreate, Token, UserRead
from app.db.models.user import User  # User ORM 모델
from app.db.session import AsyncSessionLocal
from app.core.security import create_access_token
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 회원가입입
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    # 이메일 중복 체크
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(409, "Email already registered")
    # 비밀번호 해싱
    pw_hash = hash_password(body.password)
    new_user = User(
        email=body.email,
        name=body.name,
        hashed_password=pw_hash,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserRead.from_orm(new_user)

# 로그인
@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(sub=str(user.id))
    return {"access_token": token, "token_type": "Bearer"}
