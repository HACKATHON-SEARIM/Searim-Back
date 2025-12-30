from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.database import Base


class MissionType(str, enum.Enum):
    """미션 타입 Enum"""
    DAILY = "DAILY"  # 일일 퀘스트
    SPECIAL = "SPECIAL"  # 특별 미션


class Mission(Base):
    """미션 Entity"""

    __tablename__ = "missions"

    todo_id = Column(Integer, primary_key=True, autoincrement=True, comment="미션 ID")
    todo = Column(String(255), nullable=False, comment="미션 내용")
    credits = Column(Integer, nullable=False, comment="보상 크레딧")
    mission_type = Column(SQLEnum(MissionType), default=MissionType.DAILY, nullable=False, comment="미션 타입")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")

    def __repr__(self):
        return f"<Mission(todo_id={self.todo_id}, todo={self.todo}, credits={self.credits})>"


class UserMission(Base):
    """사용자 미션 완료 기록 Entity"""

    __tablename__ = "user_missions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="기록 ID")
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="사용자 ID")
    todo_id = Column(Integer, ForeignKey("missions.todo_id"), nullable=False, index=True, comment="미션 ID")
    completed = Column(Integer, default=0, nullable=False, comment="완료 여부 (0: 미완료, 1: 완료)")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="완료 일시")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")

    def __repr__(self):
        return f"<UserMission(user_id={self.user_id}, todo_id={self.todo_id}, completed={self.completed})>"


class GarbageCollection(Base):
    """쓰레기 수집 기록 Entity"""

    __tablename__ = "garbage_collections"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="수집 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="사용자 ID")
    lat = Column(Float, nullable=False, comment="수집 위치 위도")
    lon = Column(Float, nullable=False, comment="수집 위치 경도")
    image_url = Column(String(500), nullable=True, comment="수집 사진 URL")
    credits_earned = Column(Integer, nullable=False, comment="획득 크레딧")
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), comment="수집 일시")

    def __repr__(self):
        return f"<GarbageCollection(id={self.id}, ocean_id={self.ocean_id}, user_id={self.user_id})>"
