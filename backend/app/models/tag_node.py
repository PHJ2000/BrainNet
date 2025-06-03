# backend/app/models/tag_node.py
from pydantic import BaseModel

class TagNodeOut(BaseModel):
    tag_id: int
    node_id: int

    class Config:
        from_attributes = True
