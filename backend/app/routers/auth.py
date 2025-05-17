# # backend/app/routers/auth.py

# from fastapi import APIRouter, HTTPException, Depends, status
# from fastapi.security import OAuth2PasswordRequestForm
# from pydantic import EmailStr
# from typing import Optional, Dict, Any

# from app.models import UserCreate, UserRead, Token
# from app.security import create_access_token, get_current_user_id
# from app.storage import USERS, USER_PROJECT_MAP

# import uuid
# from datetime import datetime

# router = APIRouter(prefix="/auth", tags=["Auth"])


# def _utc_now() -> str:
#     return datetime.utcnow().isoformat() + "Z"


# @router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
# def register(payload: UserCreate):
#     if any(u["email"] == payload.email for u in USERS.values()):
#         raise HTTPException(status_code=409, detail="Email already registered")
#     uid = f"user_{uuid.uuid4().hex[:6]}"
#     new_user = {
#         "id": uid,
#         "email": payload.email,
#         "name": payload.name,
#         "password": payload.password,  # ❗ in production, hash this
#         "created_at": _utc_now(),
#     }
#     USERS[uid] = new_user
#     USER_PROJECT_MAP[uid] = []
#     return {k: v for k, v in new_user.items() if k != "password"}


# @router.post("/login", response_model=Token)
# def login(form: OAuth2PasswordRequestForm = Depends()):
#     user = next((u for u in USERS.values() if u["email"] == form.username), None)
#     if not user or user["password"] != form.password:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     tk = create_access_token(sub=user["id"])
#     return {"access_token": tk, "token_type": "Bearer"}
