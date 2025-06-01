import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Path, HTTPException, status
from app.models import TagCreate, TagUpdate, TagOut
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m, get_tag as _t, get_node as _n
from app.db import store as db
from app.core.security import get_current_user_id as _uid
from app.utils.helpers   import ensure_member as _m, ensure_owner as _o, \
                               get_node as _n, get_tag as _t, get_node_by_parent_id
from app.utils.time      import utc_now as _now
from app.db              import store as db
import re, openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/projects/{project_id}/tags", tags=["Tags"])

@router.get("", response_model=List[TagOut])
def list_tags(project_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    return [t for t in db.TAGS.values() if t["project_id"] == project_id]

@router.post("", response_model=TagOut, status_code=201)
def create_tag(body: TagCreate, project_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    tid=f"tag_{uuid.uuid4().hex[:6]}"
    db.TAGS[tid]={
        "id":tid,"project_id":project_id,"name":body.name,"description":body.description,
        "color":body.color,"node_count":0,"summary":""
    }
    return db.TAGS[tid]

@router.get("/{tag_id}", response_model=TagOut)
def get_tag(project_id: str, tag_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    tag=_t(tag_id)
    if tag["project_id"]!=project_id:
        raise HTTPException(404,"Tag not in project")
    tag["nodes"]=[nid for nid, tags in db.NODE_TAG_MAP.items()
                 if tag_id in tags and db.NODES[nid]["project_id"]==project_id]
    return tag

@router.patch("/{tag_id}", response_model=TagOut)
def update_tag(body: TagUpdate, project_id: str, tag_id: str,
               uid: str = Depends(_uid)):
    _m(uid, project_id)
    tag=_t(tag_id)
    for f in ("name","description","color"):
        val=getattr(body,f)
        if val is not None:
            tag[f]=val
    return tag

@router.delete("/{tag_id}", status_code=204)
def delete_tag(project_id: str, tag_id: str, uid: str = Depends(_uid)):
    _m(uid, project_id)
    db.TAGS.pop(tag_id, None)
    for tags in db.NODE_TAG_MAP.values():
        if tag_id in tags:
            tags.remove(tag_id)
    return

@router.post("/{tag_id}/nodes/{node_id}", response_model=Dict[str, str])
def attach_tag(project_id: str, tag_id: str, node_id: str,
               uid: str = Depends(_uid)):
    _m(uid, project_id)
    node=_n(node_id, project_id)
    tag=_t(tag_id)
    if tag_id in db.NODE_TAG_MAP[node_id]:
        raise HTTPException(409,"Already attached")
    db.NODE_TAG_MAP[node_id].append(tag_id)
    tag["node_count"]+=1
    return {"tag_id":tag_id,"node_id":node_id,"status":"attached"}

@router.delete("/{tag_id}/nodes/{node_id}", response_model=Dict[str, str])
def detach_tag(project_id: str, tag_id: str, node_id: str,
               uid: str = Depends(_uid)):
    _m(uid, project_id)
    node=_n(node_id, project_id)
    if tag_id not in db.NODE_TAG_MAP[node_id]:
        raise HTTPException(400,"Node not tagged")
    db.NODE_TAG_MAP[node_id].remove(tag_id)
    db.TAGS[tag_id]["node_count"]-=1
    return {"tag_id":tag_id,"node_id":node_id,"status":"detached"}

@router.post("/{tag_id}/summary", response_model=TagOut)
def refresh_summary(project_id: str, tag_id: str,
                    uid: str = Depends(_uid)):
    _m(uid, project_id)
    tag=_t(tag_id)
    nodes = [db.NODES[nid] for nid in db.NODE_TAG_MAP
             if tag_id in db.NODE_TAG_MAP[nid] and
                db.NODES[nid]["project_id"]==project_id]
    tag["summary"]=_create_summary("\n".join(n["content"] for n in nodes[:3])) or "(empty)"

    return tag


def _create_summary(contents: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 문장들을 요약해야합니다."},
                {"role": "user", "content": f"주어지는 문장들을 2~3개 정도의 문장으로 요약해줘: {contents}"}
            ],
            max_tokens=256,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()# 메시지 파싱
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 전체 예외 스택을 콘솔에 출력
        raise HTTPException(status_code=500, detail=str(e))
    return answer

# 태그에 노드를 attach하면 해당 노드의 자식노드들 까지 전부 자동으로 attach되게 하는 함수
def _attach_nodechain_to_tag(project_id: str, tag_id: str, node_id: str,
               uid: str = Depends(_uid), visited=None):
    #_m(uid, project_id)
    if visited is None:
        visited = set()
    if node_id in visited:
        return  # 순환 방지
    visited.add(node_id)
    node=_n(node_id, project_id)
    tag=_t(tag_id)
    if tag_id in db.NODE_TAG_MAP[node_id]:
        raise HTTPException(409,"Already attached")
    db.NODE_TAG_MAP[node_id].append(tag_id)
    tag["node_count"]+=1

    chlidnodes = get_node_by_parent_id(node_id)
    if not chlidnodes :
        return
    for child in chlidnodes:
        _attach_nodechain_to_tag(project_id, tag_id, child, uid, visited) 

# 자식 노드들까지 detach하는 함수

def _dettach_nodechain_to_tag(project_id: str, tag_id: str, node_id: str,
               uid: str = Depends(_uid), visited=None):
    if visited is None:
        visited = set()
    if node_id in visited:
        return  # 순환 방지
    visited.add(node_id)
    node=_n(node_id, project_id)
    tag=_t(tag_id)
    if tag_id not in db.NODE_TAG_MAP[node_id]:
        raise HTTPException(400,"Node not tagged")
    db.NODE_TAG_MAP[node_id].remove(tag_id)
    db.TAGS[tag_id]["node_count"]-=1

    chlidnodes = get_node_by_parent_id(node_id)
    if not chlidnodes :
        return
    for child in chlidnodes:
        _dettach_nodechain_to_tag(project_id, tag_id, child, uid, visited) 
    pass
