# backend/app/routers/websocket.py

from fastapi import APIRouter, WebSocket, Query
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from app.utils.ws_manager import connect, disconnect

router = APIRouter()

@router.websocket("/projects/{project_id}/ws")
async def project_ws(
    project_id: str,
    websocket: WebSocket,
    token: str = Query(...)
):
    # 1) 토큰 검증
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise JWTError()
    except JWTError:
        # 유효하지 않은 토큰이면 연결 차단
        await websocket.close(code=4401)
        return

    # 2) WS 매니저에 연결 등록
    await connect(project_id, websocket)

    try:
        while True:
            # 필요에 따라 클라이언트가 보내는 메시지도 처리할 수 있음
            await websocket.receive_text()
    finally:
        # 연결이 끊어질 때 반드시 호출하여 clean-up
        disconnect(project_id, websocket)
