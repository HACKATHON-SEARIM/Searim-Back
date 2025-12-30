# Marine Real Estate API

해양 부동산 관리 및 거래 플랫폼 백엔드 API

## 프로젝트 소개

해양을 개인이 소유하고 관리할 수 있는 플랫폼입니다. 사용자는 해양 지역을 구매하고, 쓰레기를 수거하며, 건물을 짓고, 실시간 뉴스와 해양 데이터에 따라 변동하는 시세를 경험할 수 있습니다.

## 주요 기능

### 1. 해양 거래
- 해양 지역 구매/판매
- 해양 지역 경매
- 실시간 시세 변동

### 2. 해양 관리
- 내 해양 지역 조회
- 음식점/빌딩 건설
- 자동 수익금 지급

### 3. 미션
- 일일 퀘스트
- 해양 쓰레기 수집 (AI 이미지 인증)
- GPS 기반 미션 (바다 사진 찍기 등)

### 4. 실시간 반영
- 뉴스 기사에 따른 시세 변동
- 해양 수질 데이터 반영
- 쓰레기 수집 횟수에 따른 가치 변화

## 기술 스택

- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **AI**: Google Gemini API (이미지 인증)
- **Task Scheduler**: APScheduler

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/
```

## 프로젝트 구조

```
app/
├── main.py                 # FastAPI 애플리케이션 진입점
├── config.py              # 설정 관리
├── database.py            # 데이터베이스 연결
├── domain/                # 도메인별 구현
│   ├── auth/             # 인증/인가
│   ├── ocean/            # 해양 조회
│   ├── ocean_management/ # 해양 관리
│   ├── ocean_trade/      # 해양 거래
│   ├── mission/          # 미션
│   └── article/          # 기사
├── global/               # 전역 설정
│   ├── exception/       # 예외 처리
│   └── security/        # 보안
└── background/          # 백그라운드 작업
    └── tasks.py        # 주기적 작업
```
