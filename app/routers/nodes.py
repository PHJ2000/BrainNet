from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, deps, crud

router = APIRouter(tags=["nodes"])

@router.get("/projects/{project_id}/nodes", response_model=List[schemas.Node])
def list_nodes(project_id: str, tag_ids: str = None, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    tags = tag_ids.split(",") if tag_ids else None
    return crud.get_nodes(db, project_id, tag_ids=tags)
# :contentReference[oaicite:24]{index=24}:contentReference[oaicite:25]{index=25}

@router.post("/projects/{project_id}/nodes/{node_id}/activate", response_model=schemas.Node)
def activate_node(project_id: str, node_id: str, db: Session = Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    return crud.activate_node(db, project_id, node_id)
# :contentReference[oaicite:26]{index=26}:contentReference[oaicite:27]{index=27}
