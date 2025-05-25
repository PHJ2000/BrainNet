# backend/app/routers/history.py
from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException
from app.models import HistoryOut
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.db              import store as db

router = APIRouter(prefix="/projects/{project_id}/history", tags=["History"])

@router.get("", response_model=List[HistoryOut])
def list_history(project_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    return [h for h in db.PROJECT_HISTORY if h["project_id"] == project_id]

@router.get("/{entry_id}", response_model=HistoryOut)
def get_history(project_id: str, entry_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    entry=next((h for h in db.PROJECT_HISTORY
               if h["id"]==entry_id and h["project_id"]==project_id), None)
    if not entry:
        raise HTTPException(404,"History entry not found")
    return entry
