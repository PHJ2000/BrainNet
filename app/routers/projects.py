from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, deps, crud

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[schemas.Project])
def list_projects(db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.get_user_projects(db, user.id)
# :contentReference[oaicite:14]{index=14}:contentReference[oaicite:15]{index=15}

@router.post("", response_model=schemas.Project, status_code=201)
def create_project(p: schemas.Project, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.create_project(db, owner_id=user.id, project_in=p)
# :contentReference[oaicite:16]{index=16}:contentReference[oaicite:17]{index=17}

@router.get("/{project_id}/summary")
def project_summary(project_id: str, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.get_project_summary(db, project_id)
# :contentReference[oaicite:18]{index=18}:contentReference[oaicite:19]{index=19}

@router.get("/{project_id}/history", response_model=List[schemas.ProjectHistoryEntry])
def read_history(project_id: str, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.get_history(db, project_id)
# :contentReference[oaicite:20]{index=20}:contentReference[oaicite:21]{index=21}

@router.get("/{project_id}/history/{entry_id}", response_model=schemas.ProjectHistoryEntry)
def read_history_entry(project_id: str, entry_id: int, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.get_history_entry(db, project_id, entry_id)
# :contentReference[oaicite:22]{index=22}:contentReference[oaicite:23]{index=23}
