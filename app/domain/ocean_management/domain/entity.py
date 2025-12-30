from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.database import Base


class OceanOwnership(Base):
    """해양 소유권 Entity"""

    __tablename__ = "ocean_ownerships"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="소유권 ID")
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="사용자 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")
    square_meters = Column(Integer, nullable=False, comment="소유 평수")
    purchased_at = Column(DateTime(timezone=True), server_default=func.now(), comment="구매 일시")

    def __repr__(self):
        return f"<OceanOwnership(user_id={self.user_id}, ocean_id={self.ocean_id}, square_meters={self.square_meters})>"


class BuildingType(str, enum.Enum):
    """건물 타입 Enum"""
    STORE = "STORE"  # 음식점
    BUILDING = "BUILDING"  # 빌딩


class Building(Base):
    """건물 Entity (음식점/빌딩)"""

    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="건물 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="소유자 ID")
    building_type = Column(SQLEnum(BuildingType), nullable=False, comment="건물 타입 (STORE/BUILDING)")
    income_rate = Column(Integer, nullable=False, comment="초당 수익률 (크레딧/초)")
    last_income_generated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="마지막 수익금 지급 일시"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="건설 일시")

    def __repr__(self):
        return f"<Building(id={self.id}, type={self.building_type}, ocean_id={self.ocean_id})>"
