from fastapi import FastAPI
from .routers import auth  # 추후 추가

app = FastAPI(title="BrainShare API")
app.include_router(auth.router)  # 각 라우터 등록
