# backend/app/routers/users.py
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.models import UserRead
from app.core.security import get_current_user_id as _uid
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.db              import store as db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
def me(uid: str = Depends(_uid)):
    user = db.USERS.get(uid)
    return {k: v for k, v in user.items() if k != "password"}

@router.get("/me/tag-summaries", response_model=List[Dict[str, Any]])
def my_tag_summaries(uid: str = Depends(_uid)):
    summaries: List[Dict[str, Any]] = []
    for pid in db.USER_PROJECT_MAP.get(uid, []):
        for tag in (t for t in db.TAGS.values() if t["project_id"] == pid):
            contrib_nodes = [
                nid for nid in db.NODE_TAG_MAP
                if uid in db.NODES[nid].get("authors", []) and
                   tag["id"] in db.NODE_TAG_MAP[nid]
            ]
            summaries.append({
                "project_id": pid,
                "tag_id": tag["id"],
                "tag_name": tag["name"],
                "summary": tag.get("summary", ""),
                "nodes_contributed": len(contrib_nodes),
            })
    return summaries

def get_my_nodes():
    pass
