# 실행순서

## 실행
docker compose up --build -d

## container제거
docker compose down --remove-orphans

## 중지 및 재시작
docker compose stop
docker compose start


## 기본 주소

brainnet-frontend   localhost:3000
brainnet-backend    localhost:8000
postgres:15         localhost:5432