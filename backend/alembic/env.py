import sys
import os

# [1] 상위 경로 추가 (중요!)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# [2] DB 세션과 모델 불러오기
from app.db.session import DATABASE_URL
from app.db.models import Base

# Alembic 설정
config = context.config
fileConfig(config.config_file_name)

# 메타데이터 설정 (autogenerate 시 필요)
target_metadata = Base.metadata

# [3] 비동기 URL을 동기 URL로 변환
SYNC_DB_URL = DATABASE_URL.replace("+asyncpg", "")

# [4] 마이그레이션 (offline)
def run_migrations_offline():
    context.configure(
        url=SYNC_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# [5] 마이그레이션 (online)
def run_migrations_online():
    connectable = create_engine(
        SYNC_DB_URL,
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

# [6] 실행
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
