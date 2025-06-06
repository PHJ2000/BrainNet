# backend/app/routers/nodes.py

import uuid, re, openai, os
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.models.node import NodeCreate, NodeUpdate, NodeOut
from app.core.security import get_current_user_id as _uid
from app.utils.helpers import ensure_member as _m, ensure_owner as _o
from app.db.models.node import Node as NodeORM, NodeStateEnum
from app.db.models.tag_node import TagNode
from app.db.models.tag import Tag as TagORM
from app.db.session import AsyncSessionLocal
from app.routers.tags import get_descendant_node_ids

router = APIRouter(prefix="/projects/{project_id}/nodes", tags=["Nodes"])

openai.api_key = os.getenv("OPENAI_API_KEY")


# ── DB 세션 의존성 ───────────────────────────────────────────────────
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── 내부 유틸: AI Ghost Stub ────────────────────────────────────────────
async def _gen_ai_nodes(project_id: int,body: NodeCreate, prompt: str, db: AsyncSession, uid: str = Depends(_uid)) -> List[NodeOut]:
    """
    GPT로 유령 노드 두 개를 생성하고, 두 노드 모두 반환합니다.
    """
    nodes_created: List[NodeORM] = []

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 창의적인 아이디어를 제공하는 도우미입니다."},
                {"role": "user", "content": f"다음 주제와 관련된 새로운 아이디어를 간략한 문장 형태로 두 개 작성해줘: {prompt}"}
            ],
            max_tokens=256,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        ideas = [s for s in re.split(r'\n+', answer) if s][:2]
        cleaned = [re.sub(r'^\d+\.\s*', '', s) for s in ideas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # GHOST 노드 2개 생성
    for idx, content in enumerate(cleaned):
        new_node = NodeORM(
            project_id=project_id,
            parent_id=body.parent_id if body.parent_id not in (None, 0, "", "0") else None,
            author_id=int(uid),
            content=content,
            state=NodeStateEnum.GHOST,
            depth=body.depth or 0,
            order_index=idx,
            pos_x=body.x or 0.0,
            pos_y=body.y or 0.0,
        )
        db.add(new_node)
        await db.flush()
        nodes_created.append(new_node)

    await db.commit()
    # 두 노드 모두 refresh
    for node in nodes_created:
        await db.refresh(node)

    # 두 노드를 모두 NodeOut 형태로 변환하여 반환
    return [NodeOut.from_orm(n) for n in nodes_created]


# ── CRUD ───────────────────────────────────────────────────────────────
@router.get("", response_model=List[NodeOut])
async def list_nodes(
    project_id: int,
    tag_ids: Optional[str] = Query(None),
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    await _m(int(uid), project_id, db)

    query = select(NodeORM).where(NodeORM.project_id == project_id)

    if tag_ids:
        wanted = [int(tid) for tid in tag_ids.split(",")]
        query = (
            query.join(TagNode, NodeORM.id == TagNode.node_id)
                 .where(TagNode.tag_id.in_(wanted))
        )

    result = await db.execute(query)
    nodes = result.scalars().all()
    return [NodeOut.from_orm(n) for n in nodes]


@router.post("", response_model=List[NodeOut], status_code=status.HTTP_201_CREATED)
async def create_nodes(
    body: NodeCreate,
    project_id: int,
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    await _m(int(uid), project_id, db)

    # ✅ 1. AI 모드: ai_prompt 처리
    if body.ai_prompt:
        return await _gen_ai_nodes(project_id, body, body.ai_prompt, db, uid)

    # ✅ 2. content 필수 검사
    if not body.content:
        raise HTTPException(status_code=400, detail="content is required when ai_prompt absent")

    # ✅ 3. 루트 노드인지 확인
    is_root = body.parent_id in (None, 0, "", "0")

    if is_root:
        # ✅ 해당 프로젝트에 루트 노드가 이미 존재하는지 확인
        result = await db.execute(
            select(NodeORM).where(NodeORM.project_id == project_id, NodeORM.parent_id == None)
        )
        existing_root = result.scalars().first()
        if existing_root:
            raise HTTPException(
                status_code=409,
                detail="Root node already exists for this project."
            )

    # ✅ 4. 노드 생성
    new_node = NodeORM(
        project_id=project_id,
        parent_id=body.parent_id if not is_root else None,
        author_id=int(uid),
        content=body.content,
        state=NodeStateEnum.ACTIVE,
        depth=body.depth or 0,
        order_index=body.order or 0,
        pos_x=body.x or 0.0,
        pos_y=body.y or 0.0,
    )
    db.add(new_node)
    await db.commit()
    await db.refresh(new_node)

    # ✅ 5. 부모 태그 상속
    if body.parent_id is not None:
        parent_tags = await db.execute(
            select(TagNode.tag_id).where(TagNode.node_id == body.parent_id)
        )
        for (tag_id,) in parent_tags.all():
            tagnode = TagNode(tag_id=tag_id, node_id=new_node.id)
            db.add(tagnode)
        await db.commit()

    return [NodeOut.from_orm(new_node)]



@router.patch("/{node_id}", response_model=NodeOut)
async def update_node(
    body: NodeUpdate,
    project_id: int = Path(...),
    node_id: int = Path(...),
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    await _m(int(uid), project_id, db)

    result = await db.execute(
        select(NodeORM).where(NodeORM.id == node_id, NodeORM.project_id == project_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    updated = False
    if body.content is not None:
        node.content = body.content
        updated = True
    if body.x is not None:
        node.pos_x = body.x
        updated = True
    if body.y is not None:
        node.pos_y = body.y
        updated = True
    if body.depth is not None:
        node.depth = body.depth
        updated = True
    if body.order is not None:
        node.order_index = body.order
        updated = True

    if updated:
        await db.commit()
        await db.refresh(node)

    return NodeOut.from_orm(node)


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    project_id: int = Path(...),
    node_id: int = Path(...),
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    await _m(int(uid), project_id, db)

    # (1) 삭제할 노드 존재 여부 확인
    result = await db.execute(
        select(NodeORM).where(NodeORM.id == node_id, NodeORM.project_id == project_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # (2) 모든 자식 노드 id 리스트 수집 (자기 자신 포함)
    node_ids = await get_descendant_node_ids( node_id,db)

    # (3) 해당 노드들에 연결된 태그 관계 모두 삭제
    await db.execute(
        delete(TagNode).where(TagNode.node_id.in_(node_ids))
    )

    # (4) 실제 노드들 삭제
    await db.execute(
        delete(NodeORM).where(NodeORM.id.in_(node_ids))
    )

    await db.commit()
    return


@router.post("/{node_id}/activate", response_model=NodeOut)
async def activate_node(
    project_id: int = Path(...),
    node_id: int = Path(...),
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    await _m(int(uid), project_id, db)

    result = await db.execute(
        select(NodeORM).where(NodeORM.id == node_id, NodeORM.project_id == project_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if node.state != NodeStateEnum.GHOST:
        raise HTTPException(status_code=400, detail="Node is not in GHOST state")
    node.state = NodeStateEnum.ACTIVE

    # 1. 모든 자식 노드 조회
    node_ids = await get_descendant_node_ids(node_id,db)

    # 2. 자식 노드도 ACTIVE로 변경 (GHOST 상태만)
    await db.execute(
        update(NodeORM)
        .where(NodeORM.id.in_(node_ids), NodeORM.state == NodeStateEnum.GHOST)
        .values(state=NodeStateEnum.ACTIVE)
    )

    await db.commit()
    await db.refresh(node)
    return NodeOut.from_orm(node)


@router.post("/{node_id}/deactivate", response_model=NodeOut)
async def deactivate_node(
    project_id: int = Path(...),
    node_id: int = Path(...),
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db)
):
    await _m(int(uid), project_id, db)

    # (1) 노드 존재 확인
    result = await db.execute(
        select(NodeORM).where(NodeORM.id == node_id, NodeORM.project_id == project_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # (2) 전체 자식 노드 id 수집 (자기자신 포함)
    node_ids = await get_descendant_node_ids( node_id,db)

    # (3) ACTIVE 상태인 노드만 GHOST로 일괄 비활성화
    # bulk select
    await db.execute(
        update(NodeORM)
        .where(NodeORM.id.in_(node_ids), NodeORM.state == NodeStateEnum.ACTIVE)
        .values(state=NodeStateEnum.GHOST)
    )

    await db.commit()
    await db.refresh(node)
    return NodeOut.from_orm(node)
