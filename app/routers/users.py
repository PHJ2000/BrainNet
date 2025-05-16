from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, deps, crud

router = APIRouter(tags=["users"])

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current: schemas.User = Depends(deps.get_current_active_user)):
    return current
# :contentReference[oaicite:10]{index=10}:contentReference[oaicite:11]{index=11}

@router.get("/users/me/tag-summaries", response_model=List[schemas.TagSummary])
def read_tag_summaries(
    db: Session = Depends(deps.get_db),
    current: schemas.User = Depends(deps.get_current_active_user)
):
    return crud.get_user_tag_summaries(db, current.id)
# :contentReference[oaicite:12]{index=12}:contentReference[oaicite:13]{index=13}
