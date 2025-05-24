import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from collections import Counter
from app.models import VoteOut, HistoryOut
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m, ensure_owner as _o
from app.utils.ws_manager import broadcast
from app.utils.time import utc_now as _now
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.db              import store as db

router = APIRouter(prefix="/projects/{project_id}", tags=["Votes"])

@router.post("/tags/{tag_id}/vote", response_model=VoteOut, status_code=200)
async def cast_vote(project_id: str, tag_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    if any(v["project_id"]==project_id and v["tag_id"]==tag_id and v["user_id"]==uid
           for v in db.VOTES):
        raise HTTPException(400,"이미 투표했습니다.")
    vid=f"vote_{uuid.uuid4().hex[:6]}"
    vote={"id":vid,"project_id":project_id,"tag_id":tag_id,"user_id":uid,"voted_at":_now()}
    db.VOTES.append(vote)
    await broadcast(project_id, {"type":"vote:cast",**vote})
    return vote

@router.post("/votes/confirm", response_model=HistoryOut, status_code=200)
async def confirm_votes(project_id: str,
                        winning_tag_id: Optional[str]=Query(None),
                        uid: str = Depends(_uid)):
    _o(uid, project_id)
    pv=[v for v in db.VOTES if v["project_id"]==project_id]
    if not pv: raise HTTPException(409,"진행 중인 투표가 없습니다.")
    if winning_tag_id is None:
        winning_tag_id=Counter([v["tag_id"] for v in pv]).most_common(1)[0][0]
    summary=db.TAGS.get(winning_tag_id,{}).get("summary","")
    hid=f"hist_{uuid.uuid4().hex[:6]}"
    entry={"id":hid,"project_id":project_id,"tag_id":winning_tag_id,
           "summary":summary,"decided_at":_now(),"decided_by":uid}
    db.PROJECT_HISTORY.append(entry)
    db.VOTES[:]=[v for v in db.VOTES if v["project_id"]!=project_id]
    await broadcast(project_id, {"type":"vote:confirmed",**entry})
    return entry
