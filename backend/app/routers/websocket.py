# backend/app/routers/websocket.py
from fastapi import APIRouter, WebSocket, Query
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from app.utils.ws_manager import connect, disconnect
from app.db import store as db   # (사실 직접 쓰진 않지만 추후 확장 대비)
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.utils.time      import utc_now as _now
from app.db              import store as db

router = APIRouter()

@router.websocket("/projects/{project_id}/ws")
async def project_ws(project_id: str, websocket: WebSocket,
                     token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise JWTError()
    except JWTError:
        await websocket.close(code=4401)
        return

    await connect(project_id, websocket)
    try:
        while True:
            await websocket.receive_text()   # 필요하면 메시지 소비
    finally:
        disconnect(project_id, websocket)
