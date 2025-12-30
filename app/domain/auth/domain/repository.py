from sqlalchemy.orm import Session
from typing import Optional
from app.domain.auth.domain.entity import User


class UserRepository:
    """사용자 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_id: str, password_hash: str, credits: int = 10000) -> User:
        """
        새로운 사용자를 생성합니다.

        Args:
            user_id: 사용자 ID
            password_hash: 해싱된 비밀번호
            credits: 초기 크레딧 (기본값: 10000)

        Returns:
            User: 생성된 사용자 객체
        """
        user = User(
            user_id=user_id,
            password=password_hash,
            credits=credits
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_by_user_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[User]: 조회된 사용자 객체 또는 None
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

    def exists_by_user_id(self, user_id: str) -> bool:
        """
        사용자 ID가 존재하는지 확인합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            bool: 존재 여부
        """
        return self.db.query(User).filter(User.user_id == user_id).count() > 0
