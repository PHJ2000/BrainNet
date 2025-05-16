from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, crud, deps

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.User, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db, user_in)
# :contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = deps.create_access_token({"sub": user.id}, expires_delta=None)
    return {"access_token": access_token, "token_type": "Bearer"}
# :contentReference[oaicite:8]{index=8}:contentReference[oaicite:9]{index=9}
