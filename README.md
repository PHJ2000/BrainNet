# BrainNet

BrainNet은 아이디어를 프로젝트와 노드 단위로 정리하고, 태그와 이력을 함께 관리할 수 있는 브레인스토밍·마인드맵 서비스입니다.  
팀 프로젝트로 개발되었으며, 백엔드는 FastAPI와 PostgreSQL을 기반으로 구성했습니다.

## 주요 기능

- 회원가입 / 로그인
- JWT 기반 인증
- 사용자 정보 조회
- 프로젝트 생성 / 조회 / 수정 / 삭제
- 노드 생성 / 수정 / 삭제
- 태그 생성 / 수정 / 삭제 및 노드 연결
- 투표 기능
- 변경 이력 조회
- WebSocket 라우터 구성

## 백엔드 구조

```text
backend/
  app/
    core/       # 인증, 설정
    db/         # 세션, DB 연결
    models/     # ORM / 스키마
    routers/    # API 라우터
    utils/      # 공용 유틸리티
  alembic/      # 마이그레이션
  alembic.ini
  startup.sh
```

주요 라우터:
- `auth`
- `users`
- `projects`
- `nodes`
- `tags`
- `votes`
- `history`
- `websocket`

## 기술 스택

- Backend: FastAPI, SQLAlchemy Async, Alembic
- Database: PostgreSQL
- Auth: OAuth2PasswordBearer, JWT
- Infra: Docker, Poetry
- Frontend: Next.js

## 실행 방법

```bash
git clone https://github.com/PHJ2000/BrainNet.git
cd BrainNet

cp backend/envexample .env
cp frontend/.env.example frontend/.env.local

docker compose up --build -d
```

- Frontend: `http://localhost:3000`
- Backend Docs: `http://localhost:8000/docs`

## 참고

- 백엔드는 비동기 SQLAlchemy 세션과 Alembic 기반 마이그레이션 구조를 사용합니다.
