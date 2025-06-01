# backend/app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
import uuid

from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.models.auth import UserCreate, Token, UserRead
from app.db import store as db
from app.core.security import create_access_token
from app.utils.time import utc_now

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register(body: UserCreate):
    if any(u["email"] == body.email for u in db.USERS.values()):
        raise HTTPException(409, "Email already registered")
    uid = f"user_{uuid.uuid4().hex[:6]}"
    db.USERS[uid] = {
        "id": uid,
        "email": body.email,
        "name": body.name,
        "password": body.password,
        "created_at": utc_now(),
    }
    db.USER_PROJECT_MAP[uid] = []
    user = db.USERS[uid].copy()
    user.pop("password")
    return user

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in db.USERS.values() if u["email"] == form.username), None)
    if not user or user["password"] != form.password:
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(sub=user["id"])
    return {"access_token": token, "token_type": "Bearer"}
