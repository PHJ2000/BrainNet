from fastapi import FastAPI
from app.routers import (
    auth, users, projects, nodes, tags, votes, history, websocket
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BrainShare API", version="0.2.0")

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost:3000"] (보안 강화를 원할 경우)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, users, projects, nodes, tags, votes, history, websocket):
    app.include_router(r.router)