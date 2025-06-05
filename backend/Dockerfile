FROM python:3.12-slim

WORKDIR /app

# postgresql-client 설치
RUN apt-get update && apt-get install -y postgresql-client libpq-dev && rm -rf /var/lib/apt/lists/*

# 루트에서 pyproject.toml, poetry.lock 복사
COPY pyproject.toml poetry.lock* /app/

# Poetry 설치 및 의존성 설치
RUN pip install -U pip poetry && poetry install --no-root

# requirements.txt 복사 후 pip 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# startup.sh 복사
COPY backend/startup.sh /app/
RUN chmod +x /app/startup.sh

# 전체 백엔드 앱 복사
COPY backend/app /app/app

# alembic 폴더 및 설정 파일 복사
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini

CMD ["/app/startup.sh"]
