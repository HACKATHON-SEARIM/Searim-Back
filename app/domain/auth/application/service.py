from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status
from app.domain.auth.domain.repository import UserRepository
from app.config import get_settings

settings = get_settings()

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """인증/인가 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def signup(self, user_id: str, password: str) -> str:
        """
        회원가입을 처리합니다.

        Args:
            user_id: 사용자 ID
            password: 비밀번호 (평문)

        Returns:
            str: JWT 액세스 토큰

        Raises:
            HTTPException: 중복된 user_id가 존재하는 경우
        """
        # 중복 user_id 체크
        if self.repository.exists_by_user_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 사용자 ID입니다."
            )

        # 비밀번호 해싱
        password_hash = self._hash_password(password)

        # 사용자 생성 (초기 크레딧 10000)
        user = self.repository.create_user(
            user_id=user_id,
            password_hash=password_hash,
            credits=settings.INITIAL_CREDITS
        )

        # JWT 토큰 생성
        access_token = self._create_access_token(user_id=user.user_id)

        return access_token

    def login(self, user_id: str, password: str) -> str:
        """
        로그인을 처리합니다.

        Args:
            user_id: 사용자 ID
            password: 비밀번호 (평문)

        Returns:
            str: JWT 액세스 토큰

        Raises:
            HTTPException: 사용자가 존재하지 않거나 비밀번호가 일치하지 않는 경우
        """
        # 사용자 조회
        user = self.repository.find_by_user_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자 ID 또는 비밀번호가 올바르지 않습니다."
            )

        # 비밀번호 검증
        if not self._verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자 ID 또는 비밀번호가 올바르지 않습니다."
            )

        # JWT 토큰 생성
        access_token = self._create_access_token(user_id=user.user_id)

        return access_token

    def _hash_password(self, password: str) -> str:
        """
        비밀번호를 해싱합니다.

        Args:
            password: 평문 비밀번호

        Returns:
            str: 해싱된 비밀번호
        """
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        비밀번호를 검증합니다.

        Args:
            plain_password: 평문 비밀번호
            hashed_password: 해싱된 비밀번호

        Returns:
            bool: 비밀번호 일치 여부
        """
        return pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(self, user_id: str) -> str:
        """
        JWT 액세스 토큰을 생성합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            str: JWT 액세스 토큰
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "exp": expire
        }
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return access_token
