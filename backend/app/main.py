from fastapi import FastAPI
from app.routers import (
    auth, users, projects, nodes, tags, votes, history, websocket
)

app = FastAPI(title="BrainShare API", version="0.2.0")

for r in (auth, users, projects, nodes, tags, votes, history, websocket):
    app.include_router(r.router)
