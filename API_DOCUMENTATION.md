# Marine Real Estate API 명세서

## 목차
1. [인증/인가](#인증인가)
2. [해양 조회](#해양-조회)
3. [해양 관리](#해양-관리)
4. [해양 거래](#해양-거래)
5. [미션](#미션)
6. [기사](#기사)

---

## 인증/인가

### 1. 회원가입
```http
POST /api/auth/signup
Content-Type: application/json

{
  "user_id": "huhon",
  "password": "1234"
}
```

**응답 (201 Created)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "huhon",
  "password": "1234"
}
```

**응답 (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 해양 조회

### 1. 해양 상세 조회
```http
GET /api/ocean/{ocean_id}
```

**응답 (200 OK)**
```json
{
  "ocean_id": 145,
  "ocean_name": "해운대",
  "lat": 35.1796,
  "lon": 129.0756,
  "region": "부산광역시",
  "detail": "해운대구",
  "price_info": {
    "base_price": 1000,
    "current_price": 1200,
    "change_rate": 20.0
  },
  "water_quality": {
    "dissolved_oxygen": {
      "value": 6.8,
      "unit": "mg/L",
      "status": "normal"
    },
    "ph": {
      "value": 8.1,
      "status": "normal"
    },
    ...
  },
  "articles": [
    {
      "article_id": 23,
      "title": "해운대 해수욕장이 점점 오염되고 있다",
      "changes": "+150",
      "url": "https://example.com"
    }
  ],
  "garbage_collection": {
    "count": 1,
    "changes": "-500"
  }
}
```

---

## 해양 관리

### 1. 내 해양 지역 조회
```http
GET /api/ocean/my
Authorization: Bearer {token}
```

**응답 (200 OK)**
```json
[
  {
    "ocean_id": 145,
    "ocean_name": "해운대",
    "square_meters": 18,
    "buildings": [
      {
        "building_id": 1,
        "building_type": "STORE",
        "income_rate": 10
      }
    ]
  }
]
```

### 2. 음식점 or 빌딩 짓기
```http
POST /api/ocean/my/build
Authorization: Bearer {token}
Content-Type: application/json

{
  "ocean_id": 145,
  "build_type": "STORE"
}
```

**응답 (201 Created)**
```json
{
  "message": "음식점 또는 빌딩 생성에 성공하였습니다"
}
```

---

## 해양 거래

### 1. 구매 가능한 해양 조회
```http
GET /api/ocean/purchase?region=부산광역시&detail=수영구
Authorization: Bearer {token}
```

**응답 (200 OK)**
```json
[
  {
    "ocean_id": 143,
    "lat": 35.1796,
    "lon": 129.0756,
    "ocean_name": "서낙동강",
    "square_meters": 34,
    "credits": 8000
  }
]
```

### 2. 해양 구매
```http
POST /api/ocean/{ocean_id}/purchase
Authorization: Bearer {token}
Content-Type: application/json

{
  "square_meters": 34
}
```

**응답 (201 Created)**
```json
{
  "ownership": {
    "ocean_id": 143,
    "square_meters": 34
  },
  "remaining_credits": 7200
}
```

### 3. 해양 판매
```http
POST /api/ocean/{ocean_id}/sale
Authorization: Bearer {token}
Content-Type: application/json

{
  "square_meters": 10,
  "price": 1500
}
```

**응답 (201 Created)**
```json
{
  "sale_id": 1,
  "ocean_id": 145,
  "square_meters": 10,
  "price": 1500,
  "status": "ACTIVE"
}
```

### 4. 해양 경매
```http
POST /api/ocean/{ocean_id}/auction
Authorization: Bearer {token}
Content-Type: application/json

{
  "square_meters": 10
}
```

**응답 (201 Created)**
```json
{
  "auction_id": 1,
  "ocean_id": 145,
  "square_meters": 10,
  "starting_price": 960,
  "current_price": 960,
  "status": "ACTIVE"
}
```

---

## 미션

### 1. 미션 조회
```http
GET /api/mission
Authorization: Bearer {token}
```

**응답 (200 OK)**
```json
[
  {
    "todo_id": 2,
    "todo": "비닐 쓰레기 분리수거하기",
    "credits": 500,
    "completed": 1
  },
  {
    "todo_id": 3,
    "todo": "캔 쓰레기 1개 분리수거하기",
    "credits": 500,
    "completed": 0
  }
]
```

### 2. 미션 완료
```http
POST /api/mission/{todo_id}
Authorization: Bearer {token}
Content-Type: multipart/form-data

image: (binary file)
```

**응답 (200 OK)**
```json
{
  "message": "미션을 완료하였습니다",
  "credits_earned": 500
}
```

**응답 (400 Bad Request)**
```json
{
  "message": "미션 인증에 실패하였습니다"
}
```

### 3. 해양 쓰레기 수집하기
```http
POST /api/mission/ocean/garbage/collection?lat=35.095&lon=129.035
Authorization: Bearer {token}
Content-Type: multipart/form-data

image: (binary file)
```

**응답 (200 OK)**
```json
{
  "message": "쓰레기 수집을 완료하였습니다",
  "ocean_id": 145,
  "ocean_name": "해운대",
  "credits_earned": 100
}
```

---

## 기사

### 1. 기사 리스트 조회
```http
GET /api/article
```

**응답 (200 OK)**
```json
{
  "oceans": [
    {
      "ocean_id": 3,
      "ocean_name": "해운대",
      "articles": [
        {
          "article_id": 2,
          "ocean_id": 3,
          "ocean_name": "해운대",
          "title": "해운대 해수욕장이 점점 오염되고 있다",
          "changes": "+150",
          "url": "https://example.com"
        }
      ]
    }
  ]
}
```

---

## 인증 방식

모든 보호된 엔드포인트는 JWT Bearer 토큰을 사용합니다:

```http
Authorization: Bearer {access_token}
```

## 에러 응답

```json
{
  "message": "에러 메시지"
}
```

### HTTP 상태 코드
- `200 OK`: 성공
- `201 Created`: 리소스 생성 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `409 Conflict`: 리소스 충돌
