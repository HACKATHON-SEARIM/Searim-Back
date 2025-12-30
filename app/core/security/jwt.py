from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import get_settings
from app.core.exception.base import UnauthorizedException

settings = get_settings()

# OAuth2 스킴 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id 등)
        expires_delta: 토큰 만료 시간 (기본: 설정값 사용)

    Returns:
        생성된 JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    JWT 토큰 디코딩

    Args:
        token: JWT 토큰

    Returns:
        디코딩된 페이로드

    Raises:
        UnauthorizedException: 토큰이 유효하지 않을 때
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid token")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    현재 로그인한 사용자 ID 가져오기

    FastAPI의 Depends에서 사용됩니다.
    OAuth2PasswordBearer를 통해 Authorization 헤더에서 Bearer 토큰을 자동으로 추출하고 검증합니다.

    Args:
        token: OAuth2PasswordBearer가 자동으로 추출한 JWT 토큰

    Returns:
        사용자 ID

    Raises:
        UnauthorizedException: 토큰이 없거나 유효하지 않을 때
    """
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    return user_id
