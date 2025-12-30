from sqlalchemy.orm import Session
from typing import Optional, List
from app.domain.auth.domain.entity import User


class UserRepository:
    """사용자 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, password_hash: str, credits: int = 10000) -> User:
        """
        새로운 사용자를 생성합니다.

        Args:
            username: 사용자 이름
            password_hash: 해싱된 비밀번호
            credits: 초기 크레딧 (기본값: 10000)

        Returns:
            User: 생성된 사용자 객체
        """
        user = User(
            user_id=username,
            password=password_hash,
            credits=credits
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_by_username(self, username: str) -> Optional[User]:
        """
        사용자 이름으로 사용자를 조회합니다.

        Args:
            username: 사용자 이름

        Returns:
            Optional[User]: 조회된 사용자 객체 또는 None
        """
        return self.db.query(User).filter(User.user_id == username).first()

    def exists_by_username(self, username: str) -> bool:
        """
        사용자 이름이 존재하는지 확인합니다.

        Args:
            username: 사용자 이름

        Returns:
            bool: 존재 여부
        """
        return self.db.query(User).filter(User.user_id == username).count() > 0

    def find_top_users_by_credits(self, limit: int = 10) -> List[User]:
        """
        크레딧이 높은 순서로 사용자를 조회합니다.

        Args:
            limit: 조회할 사용자 수 (기본값: 10)

        Returns:
            List[User]: 사용자 목록 (크레딧 내림차순)
        """
        return (
            self.db.query(User)
            .order_by(User.credits.desc())
            .limit(limit)
            .all()
        )
