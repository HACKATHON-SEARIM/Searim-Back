from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    """회원가입 요청 DTO"""

    user_id: str = Field(..., description="사용자 ID", min_length=1, max_length=50)
    password: str = Field(..., description="비밀번호", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "huhon",
                "password": "1234"
            }
        }


class LoginRequest(BaseModel):
    """로그인 요청 DTO"""

    user_id: str = Field(..., description="사용자 ID", min_length=1, max_length=50)
    password: str = Field(..., description="비밀번호", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "huhon",
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
