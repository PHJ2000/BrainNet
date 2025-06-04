# backend/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import UserRead  # Pydantic
from app.db.models.user import User    # ORM
from app.db.models.project import Project
from app.db.models.tag import Tag
from app.db.models.node import Node
from app.db.models.project_user_role import ProjectUserRole
from app.db.models.tag_node import TagNode
from app.core.security import get_current_user_id as _uid
from app.db.session import AsyncSessionLocal

router = APIRouter(prefix="/users", tags=["Users"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/me", response_model=UserRead)
async def me(
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == int(uid)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me/tag-summaries", response_model=List[Dict[str, Any]])
async def my_tag_summaries(
    uid: str = Depends(_uid),
    db: AsyncSession = Depends(get_db),
):
    """
    - 사용자가 속한 모든 프로젝트를 ProjectUserRole에서 조회
    - 각 프로젝트별로 Tag 테이블을 조회
    - TagNode 매핑을 통해 '이 태그에 속한 노드들'을 조회
    - Node.author_id == uid 인 개수를 세서 nodes_contributed로 반환
    """
    # 1) 이 사용자가 속한 프로젝트 ID 목록
    projects_result = await db.execute(
        select(ProjectUserRole.project_id).where(ProjectUserRole.user_id == int(uid))
    )
    project_ids = [pid for (pid,) in projects_result.all()]

    summaries: List[Dict[str, Any]] = []
    for pid in project_ids:
        # 2) 프로젝트별 태그
        tags_result = await db.execute(
            select(Tag).where(Tag.project_id == pid)
        )
        tags = tags_result.scalars().all()

        for tag in tags:
            # 3) 이 태그에 연결된 모든 node_id 조회 (TagNode)
            node_ids_result = await db.execute(
                select(TagNode.node_id).where(TagNode.tag_id == tag.id)
            )
            node_ids_for_tag = [nid for (nid,) in node_ids_result.all()]

            if not node_ids_for_tag:
                contributed_count = 0
            else:
                # 4) 이 사용자가 작성한 노드 중, 위 node_ids_for_tag에 속하는 것만 카운트
                contrib_nodes_result = await db.execute(
                    select(func.count(Node.id)).where(
                        Node.id.in_(node_ids_for_tag),
                        Node.author_id == uid
                    )
                )
                contributed_count = contrib_nodes_result.scalar_one()

            summaries.append({
                "project_id": pid,
                "tag_id": tag.id,
                "tag_name": tag.name,
                # Tag 모델에 summary 컬럼이 있으면 사용, 없으면 빈 문자열로 처리
                "summary": getattr(tag, "summary", "") or "",
                "nodes_contributed": contributed_count,
            })

    return summaries
