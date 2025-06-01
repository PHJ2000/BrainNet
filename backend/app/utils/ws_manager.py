from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from collections import defaultdict
from typing import Dict, Set, Any, List

WS_CONNECTIONS: Dict[str, Set[WebSocket]] = defaultdict(set)

async def connect(project_id: str, ws: WebSocket):
    await ws.accept()
    WS_CONNECTIONS[project_id].add(ws)

def disconnect(project_id: str, ws: WebSocket):
    WS_CONNECTIONS[project_id].discard(ws)

async def broadcast(project_id: str, msg: Dict[str, Any]):
    dead: List[WebSocket] = []
    for ws in WS_CONNECTIONS[project_id]:
        try:
            await ws.send_json(msg)
        except WebSocketDisconnect:
            dead.append(ws)
    for ws in dead:
        disconnect(project_id, ws)
