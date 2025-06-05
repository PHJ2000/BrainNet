# BRAINNET

## 개요
## 📖 프로젝트 소개

**BRAINNET**은 GPT-4o 기반 **AI 마인드맵 엔진**으로 아이디어 발상을 ✨가속화✨하는 **싱글-유저 웹 애플리케이션**입니다.

| 핵심 기능        | 요약                                 |
| ------------ | ---------------------------------- |
| **AI 자동 확장** | 키워드 → GPT-4o가 3-5개의 관련 아이디어를 즉시 제안 |
| **그래프 시각화**  | Cytoscape.js로 노드·엣지를 드래그&드롭·확대/축소  |
| **태그 & 필터**  | 태그로 주제를 분류하고 조건별 하이라이트             |
| **히스토리 스냅샷** | 언제든 이전 상태로 되돌아갈 수 있는 변경 이력 저장      |

> ℹ️ 최종 버전에서는 **멀티테넌시**와 **동시 다중 사용자 편집** 기능을 제외했습니다.

---

## 🎯 프로젝트 목적 & 배경

원격 근무 시대에도 브레인스토밍은 **화면 공유 + 메모**나 **오프라인 포스트잇**에 의존하는 경우가 많습니다. 이 방식은

* **동시 편집이 어렵고** → 회의 흐름이 자주 끊기며
* **회의 후 별도 정리**가 필요해 생산성이 떨어지고
* **아이디어가 개인 경험에 편향**되는 한계가 있습니다.

**BRAINNET**은 다음 흐름을 **한 화면**에서 해결합니다.

```
아이디어 작성 → AI 연관 아이디어 확장 → 그래프 구조화 → 히스토리 저장
```

AI 추천으로 **창의적 사고의 폭**을 넓히고, 노드 색상·두께로 **중요도와 연관성**을 한눈에 파악하도록 도와줍니다.


---

## 🖥️ 데모 & 스크린샷

> **로컬 데모**
>
> 1. `http://localhost:3000` 접속 → 회원가입 후 로그인
> 2. 새 프로젝트 생성 후 브레인스토밍을 시작해 보세요!

> **스크린샷 / GIF**
> UI 캡처를 `README/img/` 폴더에 추가하면 더 좋은 인상을 줄 수 있습니다.

---

## 프로젝트 구성
프로젝트는 크게 프론트엔드와 백엔드로 구성되어 있으며, 각 서비스는 Docker 컨테이너 환경에서 구동됩니다.

프론트엔드: Next.js와 Cytoscape.js 기반으로 구현되어 아이디어를 노드 및 그래프 형태로 시각화합니다. 로그인, 회원가입, 대시보드, 프로젝트 관리 기능을 제공합니다.

백엔드: FastAPI와 PostgreSQL을 기반으로 RESTful API 및 실시간 WebSocket을 지원하며, 사용자 관리, 아이디어 데이터 관리, 프로젝트 히스토리 관리를 수행합니다.
### 디렉터리 구조

```
BRAINNET
├─ backend
│  ├─ alembic/           # DB 마이그레이션
│  ├─ app/
│  │  ├─ core/           # 설정·보안·의존성
│  │  ├─ db/             # 세션·CRUD 헬퍼
│  │  ├─ models/         # SQLAlchemy + Pydantic
│  │  ├─ routers/        # REST & WebSocket
│  │  └─ utils/
│  └─ envexample
└─ frontend
    ├─ public/           # 정적 리소스
    └─ src/
        ├─ app/          # Next.js 라우트(dashboard, login, register)
        ├─ features/     # Zustand 상태·API 모듈
        ├─ lib/          # axios 래퍼, 헬퍼
        └─ types/        # 공용 TS 타입

```

## 실행 방법

Docker Compose를 사용하여 프로젝트를 실행합니다.

### 실행

```bash
docker compose up --build -d
```

### 컨테이너 제거

```bash
docker compose down --volumes --remove-orphans
```

### 중지 및 재시작

```bash
docker compose stop
docker compose start
```

## 접속 주소

| 서비스               | 주소               |
| ----------------- | ---------------- |
| brainnet-frontend | `localhost:3000` |
| brainnet-backend  | `localhost:8000` |
| PostgreSQL        | `localhost:5432` |

## 환경 요구 사항

* Docker
* Docker Compose

## 📌 사용 예시 (워크플로우)

> 👩‍💻 **단일 사용자 버전** 기준 흐름입니다.
> 협업 기능은 로드맵에 포함돼 있어 향후 SaaS 버전에서 제공될 예정입니다.

1. **로그인 / 회원가입**
   브라우저에서 `http://localhost:3000` 접속 → 계정 생성 또는 로그인

2. **프로젝트 열기**

   * `새 프로젝트` 버튼으로 빈 캔버스 생성
   * 또는 대시보드에서 기존 프로젝트 선택 후 이어서 작업

3. **아이디어 입력 → AI 확장**
   중앙 노드(주제)를 작성하면 **GPT-4o**가 연관 아이디어 3-5개를 *즉시* 노드로 제안합니다.

4. **그래프 편집 & 태그 지정**

   * 노드를 **드래그&드롭**해 구조 재편성
   * `#마케팅`, `#UX` 등 태그를 달아 주제별로 하이라이트

5. **(협업 로드맵 기능) 투표 & 우선순위 결정**
   👍 / 👎 버튼으로 빠르게 피드백 → 중요 노드만 남겨 집중

6. **히스토리 스냅샷 저장**
   상단 **Save Snapshot** 클릭 → 현재 상태가 타임라인에 저장
   필요할 때 과거 스냅샷을 선택해 상태를 **Rewind** 할 수 있음

7. **프로젝트 종료 후에도 언제든 열람**
   저장된 마인드맵과 히스토리를 다시 불러와 아이디어를 이어서 발전시키거나,
   회의록·제안서에 그대로 인용 가능합니다.

> ⏱️ **소요 시간 예시**
>
> * 아이디어 입력 → AI 확장: *5초*
> * 노드 배치·태그 지정: *2\~3분*
> * 스냅샷 저장: *1초*
>   → 5분 내에 핵심 아이디어 틀 완성!

## 제한사항

* 본 최종 버전에서는 멀티테넌시와 멀티유저 기능이 제외되었습니다.

## 개발 스택

| 영역           | 사용 기술                                                                 |
| ------------ | --------------------------------------------------------------------- |
| **Frontend** | Next.js 14, React 19, TypeScript, Tailwind CSS, Cytoscape.js, Zustand |
| **Backend**  | FastAPI, Python 3.12, Uvicorn/Gunicorn, SQLAlchemy 2                  |
| **Database** | PostgreSQL 15, Alembic, LTree                                         |
| **AI**       | OpenAI GPT-4o, LangChain                                              |
| **Infra**    | Docker, Docker Compose, Nginx                                         |
| **테스트**      | Pytest, React Testing Library                                         |

## 🤝 기여 방법

1. **Fork → 새 브랜치 생성(`feature/…`)**
2. 기능 개발 후 **PR** 제출
3. PR 설명에 **변경 내용·스크린샷** 첨부
4. Maintainer 리뷰 & 머지

> 버그·기능 제안은 **GitHub Issues**에 등록해 주세요!

---

## 📄 라이선스

이 프로젝트는 **MIT License**로 배포됩니다.
자세한 내용은 `LICENSE` 파일을 확인하세요.

---

## 📬 문의

* **Issues**: 버그·기능 요청은 GitHub Issues 이용
* **Email**: [koreaworldclass@gmail.com](mailto:pjh@example.com) (프로젝트 담당)
* **Discussion**: 새로운 아이디어·제안은 GitHub Discussions에서 자유롭게 나눠 주세요!
