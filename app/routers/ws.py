from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from jose import JWTError, jwt
from ..deps import SECRET_KEY, ALGORITHM

router = APIRouter()

@router.websocket("/projects/{project_id}/ws")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    # JWT 검사 로직 (query param 또는 header)
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    # 연결 유지하며 실시간 이벤트 송수신
    while True:
        data = await websocket.receive_json()
        # 받은 이벤트를 처리 및 브로드캐스트...
        await websocket.send_json(data)
# :contentReference[oaicite:36]{index=36}:contentReference[oaicite:37]{index=37}
