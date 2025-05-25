# backend/Dockerfile

# Python 이미지 선택
FROM python:3.12-slim

# 작업 디렉토리
WORKDIR /app

# 루트에서 pyproject.toml, poetry.lock 복사
COPY pyproject.toml poetry.lock* /app/

# Poetry 설치 및 의존성 설치
RUN pip install -U pip poetry && poetry install --no-root

# requirements.txt 복사 후 pip 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 백엔드 앱 복사
COPY backend/app /app/app

# 실행 명령 또는 CMD는 필요에 따라 작성
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]




