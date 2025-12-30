from pydantic import BaseModel, Field
from datetime import datetime


class SignupRequest(BaseModel):
    """회원가입 요청 DTO"""

    username: str = Field(..., description="사용자 이름", min_length=1, max_length=50)
    password: str = Field(..., description="비밀번호", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "huhon",
                "password": "1234"
            }
        }


class LoginRequest(BaseModel):
    """로그인 요청 DTO"""

    username: str = Field(..., description="사용자 이름", min_length=1, max_length=50)
    password: str = Field(..., description="비밀번호", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "huhon",
                "password": "1234"
            }
        }


class AuthResponse(BaseModel):
    """인증 응답 DTO"""

    access_token: str = Field(..., description="JWT 액세스 토큰")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserInfoResponse(BaseModel):
    """사용자 정보 응답 DTO"""

    username: str = Field(..., description="사용자 이름")
    credits: int = Field(..., description="보유 크레딧")
    created_at: datetime = Field(..., description="가입 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "huhon",
                "credits": 10000,
                "created_at": "2025-12-30T12:00:00Z"
            }
        }


class RankingItemResponse(BaseModel):
    """랭킹 항목 응답 DTO"""

    rank: int = Field(..., description="순위")
    username: str = Field(..., description="사용자 이름")
    credits: int = Field(..., description="보유 크레딧")

    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "username": "huhon",
                "credits": 50000
            }
        }
