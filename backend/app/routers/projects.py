# backend/app/routers/projects.py
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from pydantic import EmailStr
from app.models import ProjectCreate, ProjectUpdate, ProjectOut
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m, ensure_owner as _o
from app.utils.time import utc_now as _now
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.db              import store as db

router = APIRouter(prefix="/projects", tags=["Projects"])

# ── CRUD 기본 ────────────────────────────────────────────────────────────
@router.get("", response_model=List[Dict[str, Any]])
def list_projects(uid: str = Depends(_uid), owned: Optional[bool] = Query(None)):
    projs = [p for p in db.PROJECTS.values() if uid in db.PROJECT_MEMBER_MAP.get(p["id"], [])]
    if owned:
        projs = [p for p in projs if p["owner_id"] == uid]
    return projs

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProjectOut)
def create_project(body: ProjectCreate, uid: str = Depends(_uid)):
    pid = f"proj_{uuid.uuid4().hex[:6]}"
    now = _now()
    db.PROJECTS[pid] = {
        "id": pid, "name": body.name, "description": body.description,
        "owner_id": uid, "created_at": now, "updated_at": now
    }
    db.PROJECT_MEMBER_MAP[pid] = [uid]
    db.USER_PROJECT_MAP.setdefault(uid, []).append(pid)
    return db.PROJECTS[pid]

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str = Path(...), uid: str = Depends(_uid)):
    _m(uid, project_id)
    proj = db.PROJECTS[project_id]
    proj |= {
        "member_count": len(db.PROJECT_MEMBER_MAP[project_id]),
        "node_count": len([n for n in db.NODES.values() if n["project_id"] == project_id]),
        "tag_count": len([t for t in db.TAGS.values() if t["project_id"] == project_id]),
    }
    return proj

@router.patch("/{project_id}", response_model=ProjectOut)
@router.put("/{project_id}",  response_model=ProjectOut)
def update_project(body: ProjectUpdate, project_id: str, uid: str = Depends(_uid)):
    proj = _o(uid, project_id)
    if body.name is not None:        proj["name"]        = body.name
    if body.description is not None: proj["description"] = body.description
    proj["updated_at"] = _now()
    return proj

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, uid: str = Depends(_uid)):
    _o(uid, project_id)
    db.PROJECTS.pop(project_id, None)
    db.PROJECT_MEMBER_MAP.pop(project_id, None)
    return

# ── 초대 & 참여 ──────────────────────────────────────────────────────────
@router.post("/{project_id}/invite", response_model=Dict[str, str])
def invite_project(project_id: str, email: EmailStr,
                   uid: str = Depends(_uid)):
    _o(uid, project_id)
    token = uuid.uuid4().hex
    db.INVITES[token] = {"project_id": project_id, "email": email}
    return {"invite_token": token, "message": f"Invitation sent to {email}"}

@router.post("/join", status_code=200)
def join_project(token: str = Query(...), uid: str = Depends(_uid)):
    inv = db.INVITES.pop(token, None)
    if not inv:
        raise HTTPException(400, "Invalid or used token")
    pid = inv["project_id"]
    if uid not in db.PROJECT_MEMBER_MAP[pid]:
        db.PROJECT_MEMBER_MAP[pid].append(uid)
    db.USER_PROJECT_MAP.setdefault(uid, []).append(pid)
    return {"project_id": pid, "status": "joined"}

# ── 요약 ────────────────────────────────────────────────────────────────
@router.get("/{project_id}/summary", response_model=Dict[str, Any])
def project_summary(project_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    tags = [t for t in db.TAGS.values() if t["project_id"] == project_id]
    tag_summaries = sorted(tags, key=lambda t: t.get("node_count", 0), reverse=True)
    return {
        "project_id": project_id,
        "project_name": db.PROJECTS[project_id]["name"],
        "total_nodes": len([n for n in db.NODES.values() if n["project_id"] == project_id]),
        "total_tags": len(tags),
        "tag_summaries": tag_summaries,
    }
