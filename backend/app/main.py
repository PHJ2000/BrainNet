# from fastapi import FastAPI
# from .routers import auth  # 추후 추가

# app = FastAPI(title="BrainShare API")
# app.include_router(auth.router)  # 각 라우터 등록

# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost:3000"] (보안 강화를 원할 경우)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello")
def hello():
    return {"message": "Hello from backend!"}
