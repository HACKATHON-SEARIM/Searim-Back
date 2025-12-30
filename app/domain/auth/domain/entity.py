from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """사용자 Entity"""

    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, index=True, comment="사용자 ID")
    password = Column(String(255), nullable=False, comment="비밀번호 해시")
    credits = Column(Integer, default=10000, nullable=False, comment="보유 크레딧")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 일시"
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, credits={self.credits})>"
