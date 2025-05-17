# backend/app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# DATABASE_URL = "postgresql+asyncpg://brain:pass@postgres:5432/brainshare" //이거는 docker-compose나 kube시
DATABASE_URL = "postgresql+asyncpg://brain:pass@localhost:5432/brainshare"

engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()
