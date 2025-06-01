# backend/app/routers/debug.py
from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.db              import store as db

router = APIRouter(prefix="/_debug", tags=["Debug"])

@router.get("/invites")
def invites(uid: str = Depends(get_current_user_id)):
    return db.INVITES
