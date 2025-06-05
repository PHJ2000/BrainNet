# backend/app/models/node_metrics.py
from pydantic import BaseModel
from datetime import datetime

class NodeMetricsOut(BaseModel):
    node_id: int
    subtree_size: int
    density_score: float
    updated_at: datetime

    class Config:
        from_attributes = True
