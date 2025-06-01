import uuid, random
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from app.models import NodeCreate, NodeUpdate, NodeOut
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m, get_node as _n
from app.utils.time import utc_now as _now
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t
from app.routers.tags import attach_tag, detach_tag
from app.utils.time      import utc_now as _now
from app.db              import store as db
import re, openai, os

router = APIRouter(prefix="/projects/{project_id}/nodes", tags=["Nodes"])

openai.api_key = os.getenv("OPENAI_API_KEY")
# ── 내부 유틸: AI Ghost Stub ────────────────────────────────────────────
def _gen_ai_nodes(project_id: str, prompt: str):
    nodes=[]
    print(os.getenv("OPENAI_API_KEY"))
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 창의적인 아이디어를 제공하는 도우미입니다."},
                {"role": "user", "content": f"다음 주제와 관련된 새로운 아이디어를 문장 형태로 두 개 작성해줘: {prompt}"}
            ],
            max_tokens=256,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()# 메시지 파싱
        
        ideas = [s for s in re.split(r'\n+', answer) if s]

        
        ideas = ideas[:2]
        cleaned_ideas = [re.sub(r'^\d+\.\s*', '', n) for n in ideas] # 숫자 기호 제거.

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 전체 예외 스택을 콘솔에 출력
        raise HTTPException(status_code=500, detail=str(e))
    for i in range(2):
        nid=f"node_{uuid.uuid4().hex[:6]}"
        node={
            "id":nid,"project_id":project_id,"content":f"{cleaned_ideas[i]}",
            "status":"GHOST","x":random.uniform(200,400),"y":random.uniform(200,400),
            "depth":0,"order":i,"authors":[]
        }
        db.NODES[nid]=node
        db.NODE_TAG_MAP[nid]=[]
        nodes.append(node)
    return nodes

# ── CRUD ───────────────────────────────────────────────────────────────
@router.get("", response_model=List[Dict[str, Any]])
def list_nodes(project_id: str, tag_ids: Optional[str] = Query(None),
               uid: str = Depends(_uid)):
    _m(uid, project_id)
    nodes = [n for n in db.NODES.values() if n["project_id"] == project_id]
    if tag_ids:
        wanted=set(tag_ids.split(','))
        nodes=[n for n in nodes if wanted & set(db.NODE_TAG_MAP.get(n["id"],[]))]
    return nodes

@router.post("", response_model=Any, status_code=201)
def create_node(body: NodeCreate, project_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    if body.ai_prompt:
        return _gen_ai_nodes(project_id, body.ai_prompt)
    if body.content is None:
        raise HTTPException(400, "content is required when ai_prompt absent")
    nid=f"node_{uuid.uuid4().hex[:6]}"
    node={
        "id":nid,"project_id":project_id,"content":body.content,"status":"ACTIVE",
        "x":body.x or 0.0,"y":body.y or 0.0,"depth":body.depth or 0,"order":body.order or 0,
        "authors":[uid], "parent_id": body.parent_id or None
    }
    db.NODES[nid]=node
    #만약 부모노드가 태그를 가지고 있다면, 자식 노드도 동일한 태그가 있어야한다.
    db.NODE_TAG_MAP[nid] = []
    if body.parent_id is None:
        pass
    else:
        for tag_id in db.NODE_TAG_MAP[body.parent_id]:
            attach_tag(project_id,tag_id, nid, uid)
    
    return node

@router.patch("/{node_id}", response_model=NodeOut)
def update_node(body: NodeUpdate, project_id: str, node_id: str,
                uid: str = Depends(_uid)):
    _m(uid, project_id)
    node=_n(node_id, project_id)
    for f in ("content","x","y","depth","order"):
        val=getattr(body,f)
        if val is not None:
            node[f]=val
    return node

@router.delete("/{node_id}", status_code=204)
def delete_node(project_id: str, node_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    db.NODES.pop(node_id, None)
    tags = db.NODE_TAG_MAP[node_id]
    for tag in tags:
        detach_tag(project_id,tag, node_id, uid)
    return

@router.post("/{node_id}/activate", response_model=NodeOut)
def activate_node(project_id: str, node_id: str, uid: str = Depends(_uid)):
    node=_n(node_id, project_id)
    if node["status"]!="GHOST":
        raise HTTPException(400,"Node is not in GHOST state")
    node["status"]="ACTIVE"
    return node

@router.post("/{node_id}/deactivate", response_model=NodeOut)
def deactivate_node(project_id: str, node_id: str, uid: str = Depends(_uid)):
    node=_n(node_id, project_id)
    if node["status"]!="ACTIVE":
        raise HTTPException(400,"Node is not in GHOST state")
    node["status"]="GHOST"
    return node