from fastapi import HTTPException
from app.db import store as db

def ensure_member(uid: str, project_id: str):
    if uid not in db.PROJECT_MEMBER_MAP.get(project_id, []):
        raise HTTPException(403, "Not a project member")

def ensure_owner(uid: str, project_id: str):
    proj = db.PROJECTS.get(project_id)
    if proj is None:
        raise HTTPException(404, "Project not found")
    if proj["owner_id"] != uid:
        raise HTTPException(403, "Owner permission required")
    return proj

def get_node(node_id: str, project_id: str):
    node = db.NODES.get(node_id)
    if not node or node["project_id"] != project_id:
        raise HTTPException(404, "Node not found")
    return node

def get_tag(tag_id: str):
    tag = db.TAGS.get(tag_id)
    if not tag:
        raise HTTPException(404, "Tag not found")
    return tag


