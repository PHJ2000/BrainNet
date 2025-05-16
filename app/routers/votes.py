from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import deps, crud

router = APIRouter(tags=["votes"])

@router.post("/projects/{project_id}/tags/{tag_id}/vote")
def cast_vote(project_id: str, tag_id: str, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.cast_vote(db, project_id, tag_id, user.id)
# :contentReference[oaicite:32]{index=32}:contentReference[oaicite:33]{index=33}

@router.post("/projects/{project_id}/votes/confirm")
def confirm_votes(project_id: str, winning_tag_id: str = None, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.confirm_vote(db, project_id, winning_tag_id)
# :contentReference[oaicite:34]{index=34}:contentReference[oaicite:35]{index=35}
