#  """
#  BrainShare – FastAPI implementation covering all endpoints described in the spec.
#  -----------------------------------------------------------------------------
#  • Fully self‑contained: run `uvicorn brainshare_api:app --reload` after `pip install fastapi[all] python-jose passlib[bcrypt] python-multipart`.
#  • In‑memory stores → swap with DB later.
#  • All routes follow exactly the paths / verbs / status codes requested.
#  • Swagger UI available at http://127.0.0.1:8000/docs for live validation.
#  """

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field

from typing import Any, Dict, List, Optional, Set
from fastapi import (
    Depends, FastAPI, HTTPException, Path, Query, Request, status, WebSocket
)
from fastapi.websockets import WebSocketDisconnect
from collections import defaultdict



# --- NEW --------------------------------------------------------------------
#  • 투표 저장소
VOTES: List[Dict[str, Any]] = []               # [{id, project_id, tag_id, user_id, voted_at}]
#  • 프로젝트 히스토리
PROJECT_HISTORY: List[Dict[str, Any]] = []     # [{id, project_id, tag_id, summary, decided_at, decided_by}]
#  • WebSocket 연결: project_id ➜ set[WebSocket]
WS_CONNECTIONS: Dict[str, Set[WebSocket]] = defaultdict(set)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Security helpers (JWT Bearer)
# ---------------------------------------------------------------------------
SECRET_KEY = "CHANGE_ME_TO_A_RANDOM_SECRET"  # 🔒
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def create_access_token(sub: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": sub, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exc
        return sub
    except JWTError:
        raise credentials_exc

# ---------------------------------------------------------------------------
# In‑memory persistence (replace with DB layer later)
# ---------------------------------------------------------------------------
USERS: Dict[str, Dict[str, Any]] = {}
PROJECTS: Dict[str, Dict[str, Any]] = {}
NODES: Dict[str, Dict[str, Any]] = {}          # keyed by node_id
TAGS: Dict[str, Dict[str, Any]] = {}           # keyed by tag_id
USER_PROJECT_MAP: Dict[str, List[str]] = {}    # user_id ➜ [project_ids]
PROJECT_MEMBER_MAP: Dict[str, List[str]] = {}  # project_id ➜ [user_ids]
NODE_TAG_MAP: Dict[str, List[str]] = {}        # node_id ➜ [tag_ids]
class UserRead(BaseModel):
     created_at: str

# ------------------------- NEW (vote / history) -----------------------------
class VoteOut(BaseModel):
    id: str
    project_id: str
    tag_id: str
    user_id: str
    voted_at: str

class HistoryOut(BaseModel):
    id: str
    project_id: str
    tag_id: str
    summary: str
    decided_at: str
    decided_by: str

# ---------------------------------------------------------------------------
# Pydantic models – Auth
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class UserRead(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    created_at: str

# ---------------------------------------------------------------------------
# Pydantic models – Project / Node / Tag (request bodies)
# ---------------------------------------------------------------------------
class ProjectCreate(BaseModel):
    name: str = Field(..., example="새 프로젝트")
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class NodeCreate(BaseModel):
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    depth: Optional[int] = 0
    order: Optional[int] = 0
    ai_prompt: Optional[str] = None

class NodeUpdate(BaseModel):
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    depth: Optional[int] = None
    order: Optional[int] = None

class TagCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

# ---------------------------------------------------------------------------
# FastAPI instance & Routers
# ---------------------------------------------------------------------------
app = FastAPI(title="BrainShare API", version="0.1.0")
# ----------------------------- REAL-TIME WS ----------------------------------
@app.websocket("/projects/{project_id}/ws")
async def project_ws(project_id: str, websocket: WebSocket, token: str = Query(...)):
    """
    클라이언트 → ws://HOST/projects/{project_id}/ws?token=JWT
    (JWT 는 /auth/login 으로 받은 access_token 그대로)
    """
    # 토큰 검증
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str | None = payload.get("sub")
        if not uid:
            raise ValueError
    except Exception:
        await websocket.close(code=4401)  # 401 비슷한 커스텀 코드
        return

    await _ws_connect(project_id, websocket)
    try:
        while True:
            # 클라이언트 메시지를 쓰려면 여기서 receive_json() 등 사용
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _ws_disconnect(project_id, websocket)

# ----------------------------- AUTH ----------------------------------------
@app.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register(payload: UserCreate):
    if any(u["email"] == payload.email for u in USERS.values()):
        raise HTTPException(status_code=409, detail="Email already registered")
    uid = f"user_{uuid.uuid4().hex[:6]}"
    new_user = {
        "id": uid,
        "email": payload.email,
        "name": payload.name,
        "password": payload.password,  # ❗️hash in prod
        "created_at": _utc_now(),
    }
    USERS[uid] = new_user
    USER_PROJECT_MAP[uid] = []
    return {k: v for k, v in new_user.items() if k != "password"}


# @app.post("/auth/login", response_model=Token) 기존 docs 보여주기용
# def login(body: UserLogin):
#     user = next((u for u in USERS.values() if u["email"] == body.email), None)
#     if not user or user["password"] != body.password:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     tk = create_access_token(sub=user["id"])
#     return {"access_token": tk, "token_type": "Bearer"}

@app.post("/auth/login", response_model=Token) # 보여주기용
def login(form: OAuth2PasswordRequestForm = Depends()):
    # OAuth2 Password flow expects `username` & `password` form fields
    user = next((u for u in USERS.values() if u["email"] == form.username), None)
    if not user or user["password"] != form.password:
        raise HTTPException(401, "Invalid credentials")
    tk = create_access_token(sub=user["id"])
    return {"access_token": tk, "token_type": "Bearer"}

# ----------------------------- USERS ---------------------------------------
@app.get("/users/me", response_model=UserRead)
def me(uid: str = Depends(get_current_user_id)):
    user = USERS.get(uid)
    return {k: v for k, v in user.items() if k != "password"}

@app.get("/users/me/tag-summaries", response_model=List[Dict[str, Any]])
def my_tag_summaries(uid: str = Depends(get_current_user_id)):
    summaries: List[Dict[str, Any]] = []
    for pid in USER_PROJECT_MAP.get(uid, []):
        for tag in (t for t in TAGS.values() if t["project_id"] == pid):
            contrib_nodes = [nid for nid in NODE_TAG_MAP if uid in NODES[nid].get("authors", []) and tag["id"] in NODE_TAG_MAP[nid]]
            summaries.append({
                "project_id": pid,
                "tag_id": tag["id"],
                "tag_name": tag["name"],
                "summary": tag.get("summary", ""),
                "nodes_contributed": len(contrib_nodes),
            })
    return summaries

# ----------------------------- PROJECTS ------------------------------------
@app.get("/projects", response_model=List[Dict[str, Any]])
def list_projects(uid: str = Depends(get_current_user_id), owned: Optional[bool] = Query(None)):
    projects = [p for p in PROJECTS.values() if uid in PROJECT_MEMBER_MAP.get(p["id"], [])]
    if owned is True:
        projects = [p for p in projects if p["owner_id"] == uid]
    return projects

@app.post("/projects", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def create_project(body: ProjectCreate, uid: str = Depends(get_current_user_id)):
    pid = f"proj_{uuid.uuid4().hex[:6]}"
    now = _utc_now()
    proj = {
        "id": pid,
        "name": body.name,
        "description": body.description,
        "owner_id": uid,
        "created_at": now,
        "updated_at": now,
    }
    PROJECTS[pid] = proj
    # membership
    PROJECT_MEMBER_MAP[pid] = [uid]
    USER_PROJECT_MAP[uid].append(pid)
    return proj

@app.get("/projects/{project_id}", response_model=Dict[str, Any])
def get_project(project_id: str = Path(...), uid: str = Depends(get_current_user_id)):
    proj = PROJECTS.get(project_id)
    _ensure_member(uid, project_id)
    proj_stats = proj | {
        "member_count": len(PROJECT_MEMBER_MAP[project_id]),
        "node_count": len([n for n in NODES.values() if n["project_id"] == project_id]),
        "tag_count": len([t for t in TAGS.values() if t["project_id"] == project_id]),
    }
    return proj_stats

@app.put("/projects/{project_id}", response_model=Dict[str, Any])
@app.patch("/projects/{project_id}", response_model=Dict[str, Any])
def update_project(body: ProjectUpdate, project_id: str = Path(...), uid: str = Depends(get_current_user_id)):
    proj = _ensure_owner(uid, project_id)
    if body.name is not None:
        proj["name"] = body.name
    if body.description is not None:
        proj["description"] = body.description
    proj["updated_at"] = _utc_now()
    return proj

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str = Path(...), uid: str = Depends(get_current_user_id)):
    _ensure_owner(uid, project_id)
    PROJECTS.pop(project_id, None)
    PROJECT_MEMBER_MAP.pop(project_id, None)
    return

"""@app.post("/projects/{project_id}/invite", response_model=Dict[str, str])
def invite(project_id: str, email: EmailStr, uid: str = Depends(get_current_user_id)):
    _ensure_owner(uid, project_id)
    # simple token
    token = uuid.uuid4().hex
    return {"invite_token": token, "message": f"Invitation sent to {email}"}"""

@app.get("/projects/{project_id}/summary", response_model=Dict[str, Any])
def project_summary(project_id: str = Path(...), uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    tags = [t for t in TAGS.values() if t["project_id"] == project_id]
    tag_summaries = sorted(tags, key=lambda t: t.get("node_count", 0), reverse=True)
    return {
        "project_id": project_id,
        "project_name": PROJECTS[project_id]["name"],
        "total_nodes": len([n for n in NODES.values() if n["project_id"] == project_id]),
        "total_tags": len(tags),
        "tag_summaries": tag_summaries,
    }

# ----------------------------- NODES ---------------------------------------
@app.get("/projects/{project_id}/nodes", response_model=List[Dict[str, Any]])
def list_nodes(project_id: str, tag_ids: Optional[str] = Query(None), uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    nodes = [n for n in NODES.values() if n["project_id"] == project_id]
    if tag_ids:
        wanted = set(tag_ids.split(','))
        nodes = [n for n in nodes if wanted & set(NODE_TAG_MAP.get(n["id"], []))]
    return nodes

@app.post("/projects/{project_id}/nodes", response_model=Any, status_code=status.HTTP_201_CREATED)
def create_node(body: NodeCreate, project_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    if body.ai_prompt:
        # pretend AI returns two ghost nodes
        return _generate_ai_nodes(project_id, body.ai_prompt)
    if body.content is None:
        raise HTTPException(400, "content is required when ai_prompt absent")
    nid = f"node_{uuid.uuid4().hex[:6]}"
    node = {
        "id": nid,
        "project_id": project_id,
        "content": body.content,
        "status": "ACTIVE",
        "x": body.x or 0.0,
        "y": body.y or 0.0,
        "depth": body.depth or 0,
        "order": body.order or 0,
        "authors": [uid],
    }
    NODES[nid] = node
    NODE_TAG_MAP[nid] = []
    return node

@app.patch("/projects/{project_id}/nodes/{node_id}", response_model=Dict[str, Any])
def update_node(body: NodeUpdate, project_id: str, node_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    node = _get_node(node_id, project_id)
    for field in ("content", "x", "y", "depth", "order"):
        val = getattr(body, field)
        if val is not None:
            node[field] = val
    return node

@app.delete("/projects/{project_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(project_id: str, node_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    NODES.pop(node_id, None)
    NODE_TAG_MAP.pop(node_id, None)
    return

@app.post("/projects/{project_id}/nodes/{node_id}/activate", response_model=Dict[str, Any])
def activate_node(project_id: str, node_id: str, uid: str = Depends(get_current_user_id)):
    node = _get_node(node_id, project_id)
    if node["status"] != "GHOST":
        raise HTTPException(400, "Node is not in GHOST state")
    node["status"] = "ACTIVE"
    return node

# ----------------------------- TAGS ----------------------------------------
@app.get("/projects/{project_id}/tags", response_model=List[Dict[str, Any]])
def list_tags(project_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    return [t for t in TAGS.values() if t["project_id"] == project_id]

@app.post("/projects/{project_id}/tags", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_tag(body: TagCreate, project_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    tid = f"tag_{uuid.uuid4().hex[:6]}"
    tag = {
        "id": tid,
        "project_id": project_id,
        "name": body.name,
        "description": body.description,
        "color": body.color,
        "node_count": 0,
        "summary": "",
    }
    TAGS[tid] = tag
    return tag

@app.get("/projects/{project_id}/tags/{tag_id}", response_model=Dict[str, Any])
def get_tag(project_id: str, tag_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    tag = _get_tag(tag_id)
    if tag["project_id"] != project_id:
        raise HTTPException(404, "Tag not in project")
    tag["nodes"] = [nid for nid, tags in NODE_TAG_MAP.items() if tag_id in tags and NODES[nid]["project_id"] == project_id]
    return tag

@app.patch("/projects/{project_id}/tags/{tag_id}", response_model=Dict[str, Any])
def update_tag(body: TagUpdate, project_id: str, tag_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    tag = _get_tag(tag_id)
    for field in ("name", "description", "color"):
        val = getattr(body, field)
        if val is not None:
            tag[field] = val
    return tag

@app.delete("/projects/{project_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(project_id: str, tag_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    TAGS.pop(tag_id, None)
    for tags in NODE_TAG_MAP.values():
        if tag_id in tags:
            tags.remove(tag_id)
    return

@app.post("/projects/{project_id}/tags/{tag_id}/nodes/{node_id}", response_model=Dict[str, str])
def attach_tag(project_id: str, tag_id: str, node_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    node = _get_node(node_id, project_id)
    tag = _get_tag(tag_id)
    if tag["project_id"] != project_id:
        raise HTTPException(404, "Tag not in project")
    if tag_id in NODE_TAG_MAP[node_id]:
        raise HTTPException(409, "Already attached")
    NODE_TAG_MAP[node_id].append(tag_id)
    tag["node_count"] += 1
    return {"tag_id": tag_id, "node_id": node_id, "status": "attached"}

@app.delete("/projects/{project_id}/tags/{tag_id}/nodes/{node_id}", response_model=Dict[str, str])
def detach_tag(project_id: str, tag_id: str, node_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    node = _get_node(node_id, project_id)
    if tag_id not in NODE_TAG_MAP[node_id]:
        raise HTTPException(400, "Node not tagged")
    NODE_TAG_MAP[node_id].remove(tag_id)
    TAGS[tag_id]["node_count"] -= 1
    return {"tag_id": tag_id, "node_id": node_id, "status": "detached"}

@app.post("/projects/{project_id}/tags/{tag_id}/summary", response_model=Dict[str, Any])
def update_summary(project_id: str, tag_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    tag = _get_tag(tag_id)
    # naive summarizer: concat first 3 node contents
    nodes = [NODES[nid] for nid in NODE_TAG_MAP if tag_id in NODE_TAG_MAP[nid] and NODES[nid]["project_id"] == project_id]
    summary_text = "\n".join(n["content"] for n in nodes[:3])
    tag["summary"] = summary_text or "(empty)"
    return tag
# ----------------------------- VOTES ----------------------------------------
@app.post("/projects/{project_id}/tags/{tag_id}/vote",
          response_model=VoteOut, status_code=200)
async def cast_vote(project_id: str, tag_id: str,
                    uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    if any(v["project_id"] == project_id and v["tag_id"] == tag_id and v["user_id"] == uid for v in VOTES):
        raise HTTPException(400, "이미 투표했습니다.")

    vid = f"vote_{uuid.uuid4().hex[:6]}"
    vote = {
        "id": vid,
        "project_id": project_id,
        "tag_id": tag_id,
        "user_id": uid,
        "voted_at": _utc_now(),
    }
    VOTES.append(vote)

    # 실시간 브로드캐스트
    await _ws_broadcast(project_id, {"type": "vote:cast", **vote})

    return vote


@app.post("/projects/{project_id}/votes/confirm",
          response_model=HistoryOut, status_code=200)
async def confirm_votes(project_id: str,
                        winning_tag_id: Optional[str] = Query(None),
                        uid: str = Depends(get_current_user_id)):
    _ensure_owner(uid, project_id)  # 프로젝트 소유자만 확정
    project_votes = [v for v in VOTES if v["project_id"] == project_id]
    if not project_votes:
        raise HTTPException(409, "진행 중인 투표가 없습니다.")

    # 가장 많은 표를 받은 태그
    if winning_tag_id is None:
        from collections import Counter
        winning_tag_id = Counter([v["tag_id"] for v in project_votes]).most_common(1)[0][0]

    # 태그 요약 가져오기 (없으면 빈 문자열)
    summary = TAGS.get(winning_tag_id, {}).get("summary", "")

    hid = f"hist_{uuid.uuid4().hex[:6]}"
    entry = {
        "id": hid,
        "project_id": project_id,
        "tag_id": winning_tag_id,
        "summary": summary,
        "decided_at": _utc_now(),
        "decided_by": uid,
    }
    PROJECT_HISTORY.append(entry)

    # 해당 프로젝트 투표 기록 초기화
    VOTES[:] = [v for v in VOTES if v["project_id"] != project_id]

    await _ws_broadcast(project_id, {"type": "vote:confirmed", **entry})
    return entry


# ----------------------------- HISTORY --------------------------------------
@app.get("/projects/{project_id}/history", response_model=List[HistoryOut])
def list_history(project_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    return [h for h in PROJECT_HISTORY if h["project_id"] == project_id]


@app.get("/projects/{project_id}/history/{entry_id}", response_model=HistoryOut)
def get_history_entry(project_id: str, entry_id: str, uid: str = Depends(get_current_user_id)):
    _ensure_member(uid, project_id)
    entry = next((h for h in PROJECT_HISTORY if h["id"] == entry_id and h["project_id"] == project_id), None)
    if not entry:
        raise HTTPException(404, "History entry not found")
    return entry

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# WebSocket helpers
# ---------------------------------------------------------------------------
async def _ws_connect(project_id: str, ws: WebSocket):
    await ws.accept()
    WS_CONNECTIONS[project_id].add(ws)

def _ws_disconnect(project_id: str, ws: WebSocket):
    WS_CONNECTIONS[project_id].discard(ws)

async def _ws_broadcast(project_id: str, message: Dict[str, Any]):
    """모든 연결에 JSON 브로드캐스트 (에러 시 연결 제거)."""
    dead: List[WebSocket] = []
    for ws in WS_CONNECTIONS[project_id]:
        try:
            await ws.send_json(message)
        except WebSocketDisconnect:
            dead.append(ws)
    for ws in dead:
        _ws_disconnect(project_id, ws)


def _ensure_member(uid: str, project_id: str):
    if uid not in PROJECT_MEMBER_MAP.get(project_id, []):
        raise HTTPException(403, "Not a project member")


def _ensure_owner(uid: str, project_id: str):
    proj = PROJECTS.get(project_id)
    if proj is None:
        raise HTTPException(404, "Project not found")
    if proj["owner_id"] != uid:
        raise HTTPException(403, "Owner permission required")
    return proj


def _get_node(node_id: str, project_id: str):
    node = NODES.get(node_id)
    if not node or node["project_id"] != project_id:
        raise HTTPException(404, "Node not found")
    return node


def _get_tag(tag_id: str):
    tag = TAGS.get(tag_id)
    if not tag:
        raise HTTPException(404, "Tag not found")
    return tag


def _generate_ai_nodes(project_id: str, prompt: str):
    """Stub AI that returns two ghost nodes."""
    nodes = []
    for i in range(2):
        nid = f"node_{uuid.uuid4().hex[:6]}"
        node = {
            "id": nid,
            "project_id": project_id,
            "content": f"AI 제안 아이디어 {i+1}",
            "status": "GHOST",
            "x": 400.0 + i * 20,
            "y": 300.0 + i * 20,
            "depth": 0,
            "order": i,
            "authors": [],
        }
        NODES[nid] = node
        NODE_TAG_MAP[nid] = []
        nodes.append(node)
    return nodes

# ---------------------------------------------------------------------------
# Run: `uvicorn brainshare_api:app --reload`
# ---------------------------------------------------------------------------


## New Version code

# 전역 컨테이너 하나 더
INVITES: Dict[str, Dict[str, str]] = {}   # token ➜ {"project_id":..., "email":...}

# (1) Owner 가 초대 토큰 생성
@app.post("/projects/{project_id}/invite", response_model=Dict[str, str])
def invite(project_id: str, email: EmailStr, uid: str = Depends(get_current_user_id)):
    _ensure_owner(uid, project_id)
    token = uuid.uuid4().hex
    INVITES[token] = {"project_id": project_id, "email": email}
    return {"invite_token": token, "message": f"Invitation sent to {email}"}

# (2) 초대받은 사용자가 토큰으로 참여
@app.post("/projects/join", status_code=200)
def join_project(token: str = Query(...), uid: str = Depends(get_current_user_id)):
    inv = INVITES.pop(token, None)
    if not inv:
        raise HTTPException(400, "Invalid or used token")
    pid = inv["project_id"]
    if uid not in PROJECT_MEMBER_MAP[pid]:
        PROJECT_MEMBER_MAP[pid].append(uid)
    USER_PROJECT_MAP.setdefault(uid, []).append(pid)
    return {"project_id": pid, "status": "joined"}



@app.get("/_debug/invites")     # 🔒 인증 붙여도 되고 그냥 둬도 OK
def dbg_invites():
    return INVITES
