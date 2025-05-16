from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, deps, crud

router = APIRouter(tags=["tags"])

@router.get("/projects/{project_id}/tags", response_model=List[schemas.Tag])
def list_tags(project_id: str, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.get_tags(db, project_id)
# :contentReference[oaicite:28]{index=28}:contentReference[oaicite:29]{index=29}

@router.post("/projects/{project_id}/tags/{tag_id}/summary")
def update_summary(project_id: str, tag_id: str, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.generate_tag_summary(db, project_id, tag_id)
# :contentReference[oaicite:30]{index=30}:contentReference[oaicite:31]{index=31}
