# Marine Real Estate API 설치 가이드

## 1. 시스템 요구사항

- Python 3.9 이상
- MySQL 8.0 이상
- pip (Python 패키지 관리자)

---

## 2. MySQL 데이터베이스 설정

### 2-1. MySQL 설치 확인

```bash
mysql --version
```

### 2-2. MySQL 접속

```bash
mysql -u root -p
```

### 2-3. 데이터베이스 생성

MySQL에 접속한 후 다음 명령어 실행:

```sql
-- 데이터베이스 생성
CREATE DATABASE marine_real_estate
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 데이터베이스 확인
SHOW DATABASES;

-- 데이터베이스 선택
USE marine_real_estate;
```

또는 제공된 SQL 스크립트 실행:

```bash
mysql -u root -p < setup_db.sql
```

### 2-4. 사용자 생성 (선택사항 - 보안 권장)

```sql
-- 전용 사용자 생성
CREATE USER 'marine_user'@'localhost' IDENTIFIED BY 'strong_password_here';

-- 권한 부여
GRANT ALL PRIVILEGES ON marine_real_estate.* TO 'marine_user'@'localhost';

-- 권한 적용
FLUSH PRIVILEGES;
```

---

## 3. Python 환경 설정

### 3-1. 가상환경 생성

```bash
# 프로젝트 디렉토리로 이동
cd /Users/huhon/projects/MarineRealEstate

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

### 3-2. 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. 환경 변수 설정

### 4-1. .env 파일 수정

`.env` 파일을 열고 다음 정보를 실제 값으로 수정:

```bash
# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/marine_real_estate?charset=utf8mb4

# 또는 별도 사용자 생성했다면:
# DATABASE_URL=mysql+pymysql://marine_user:your_password@localhost:3306/marine_real_estate?charset=utf8mb4

# JWT 비밀키 (강력한 키로 변경!)
SECRET_KEY=your-super-secret-key-change-this-in-production-$(openssl rand -hex 32)

# Gemini API 키 (https://makersuite.google.com/app/apikey 에서 발급)
GEMINI_API_KEY=your-gemini-api-key-here

# 뉴스 API 키 (https://newsapi.org/ 에서 발급 - 선택사항)
NEWS_API_KEY=your-news-api-key-here
```

### 4-2. API 키 발급 방법

#### Gemini API 키 발급
1. https://makersuite.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 키를 `.env` 파일의 `GEMINI_API_KEY`에 입력

#### News API 키 발급 (선택사항)
1. https://newsapi.org/ 접속
2. 계정 생성
3. API 키 확인
4. `.env` 파일의 `NEWS_API_KEY`에 입력

---

## 5. 데이터베이스 테이블 생성

### 5-1. Python에서 자동 생성

애플리케이션 실행 시 자동으로 테이블이 생성됩니다:

```bash
# 서버 실행 (테이블 자동 생성)
uvicorn app.main:app --reload
```

서버 시작 시 모든 테이블이 자동으로 생성됩니다!

### 5-2. 테이블 생성 확인

MySQL에서 확인:

```sql
USE marine_real_estate;
SHOW TABLES;

-- 예상 테이블 목록:
-- users
-- oceans
-- water_qualities
-- ocean_ownerships
-- buildings
-- ocean_sales
-- ocean_auctions
-- auction_bids
-- missions
-- user_missions
-- garbage_collections
-- articles
```

---

## 6. 서버 실행

```bash
# 개발 모드 (자동 재시작)
uvicorn app.main:app --reload

# 또는 특정 포트 지정
uvicorn app.main:app --reload --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

서버가 실행되면:
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## 7. 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/

# 상세 출력
pytest -v

# 특정 테스트만 실행
pytest tests/test_auth.py
```

---

## 8. 초기 데이터 생성 (선택사항)

### 8-1. 테스트 사용자 생성

API를 통해 회원가입:

```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "password": "test1234"}'
```

### 8-2. 테스트 해양 데이터 생성

MySQL에서 직접 삽입:

```sql
USE marine_real_estate;

INSERT INTO oceans (ocean_name, lat, lon, region, detail, base_price, current_price, total_square_meters, available_square_meters)
VALUES
('해운대', 35.1588, 129.1603, '부산광역시', '해운대구', 1000, 1000, 1000, 1000),
('광안리', 35.1532, 129.1186, '부산광역시', '수영구', 900, 900, 800, 800),
('송정해수욕장', 35.1786, 129.1997, '부산광역시', '해운대구', 800, 800, 600, 600);

-- 확인
SELECT * FROM oceans;
```

---

## 9. 문제 해결

### 9-1. MySQL 연결 오류

```
Error: Can't connect to MySQL server
```

**해결방법:**
1. MySQL 서비스 실행 확인:
   ```bash
   # macOS (Homebrew)
   brew services start mysql

   # Linux
   sudo systemctl start mysql

   # Windows
   net start MySQL80
   ```

2. 포트 확인 (기본 3306):
   ```bash
   mysql -u root -p --port=3306
   ```

3. `.env` 파일의 DATABASE_URL 확인

### 9-2. 인코딩 오류

```
UnicodeEncodeError
```

**해결방법:**
- `.env` 파일의 DATABASE_URL에 `?charset=utf8mb4` 추가
- MySQL 데이터베이스가 `utf8mb4`로 생성되었는지 확인

### 9-3. Import 오류

```
ModuleNotFoundError: No module named 'app'
```

**해결방법:**
```bash
# 프로젝트 루트에서 실행
cd /Users/huhon/projects/MarineRealEstate

# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 또는 가상환경 재활성화
deactivate
source venv/bin/activate
```

### 9-4. 테이블이 생성되지 않음

**해결방법:**
1. `app/database.py`의 `init_db()` 함수 확인
2. 서버 시작 로그 확인
3. 수동으로 Python에서 실행:
   ```python
   from app.database import init_db
   init_db()
   ```

---

## 10. 다음 단계

1. ✅ API 문서 확인: http://localhost:8000/docs
2. ✅ 회원가입/로그인 테스트
3. ✅ 해양 데이터 조회 테스트
4. ✅ 기능별 API 테스트
5. ✅ Gemini API 연동 테스트

---

## 11. 유용한 명령어

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행 (개발 모드)
uvicorn app.main:app --reload

# 테스트 실행
pytest

# MySQL 접속
mysql -u root -p marine_real_estate

# 로그 확인
tail -f logs/app.log  # 로그 파일 설정 시

# 의존성 업데이트
pip install --upgrade -r requirements.txt
```

---

설치 중 문제가 발생하면 이 가이드를 참고하세요!
