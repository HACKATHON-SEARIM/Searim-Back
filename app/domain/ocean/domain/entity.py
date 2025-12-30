from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class Ocean(Base):
    """해양 Entity"""

    __tablename__ = "oceans"

    ocean_id = Column(Integer, primary_key=True, autoincrement=True, comment="해양 ID")
    ocean_name = Column(String(100), nullable=False, index=True, comment="해양 이름")
    lat = Column(Float, nullable=False, comment="위도")
    lon = Column(Float, nullable=False, comment="경도")
    region = Column(String(50), nullable=False, index=True, comment="시/도")
    detail = Column(String(50), nullable=False, index=True, comment="구/군")
    base_price = Column(Integer, default=1000, nullable=False, comment="기본 가격 (1평당)")
    current_price = Column(Integer, default=1000, nullable=False, comment="현재 가격 (1평당)")
    total_square_meters = Column(Integer, default=100, nullable=False, comment="총 평수")
    available_square_meters = Column(Integer, default=100, nullable=False, comment="구매 가능한 평수")
    garbage_collection_count = Column(Integer, default=0, nullable=False, comment="쓰레기 수집 횟수")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 일시"
    )

    def __repr__(self):
        return f"<Ocean(ocean_id={self.ocean_id}, name={self.ocean_name}, price={self.current_price})>"


class WaterQualityStatus(str, enum.Enum):
    """수질 상태 Enum"""
    NORMAL = "normal"
    WARNING = "warning"
    DANGER = "danger"


class WaterQuality(Base):
    """수질 데이터 Entity"""

    __tablename__ = "water_qualities"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="수질 데이터 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")

    # 용존산소
    dissolved_oxygen_value = Column(Float, comment="용존산소 농도 (mg/L)")
    dissolved_oxygen_status = Column(SQLEnum(WaterQualityStatus), default=WaterQualityStatus.NORMAL, comment="용존산소 상태")

    # pH
    ph_value = Column(Float, comment="pH 값")
    ph_status = Column(SQLEnum(WaterQualityStatus), default=WaterQualityStatus.NORMAL, comment="pH 상태")

    # 영양염류 (부영양화 지표)
    nitrogen_value = Column(Float, comment="질소 농도 (mg/L)")
    nitrogen_status = Column(SQLEnum(WaterQualityStatus), default=WaterQualityStatus.NORMAL, comment="질소 상태")

    phosphorus_value = Column(Float, comment="인 농도 (mg/L)")
    phosphorus_status = Column(SQLEnum(WaterQualityStatus), default=WaterQualityStatus.NORMAL, comment="인 상태")

    # 탁도
    turbidity_value = Column(Float, comment="탁도 (NTU)")
    turbidity_status = Column(SQLEnum(WaterQualityStatus), default=WaterQualityStatus.NORMAL, comment="탁도 상태")

    # 오염물질
    heavy_metals_detected = Column(Integer, default=0, comment="중금속 검출 여부 (0: 미검출, 1: 검출)")
    oil_spill_detected = Column(Integer, default=0, comment="유류 오염 여부 (0: 미검출, 1: 검출)")

    # 가격 변동
    price_change = Column(Integer, default=0, comment="수질에 따른 가격 변동")

    measured_at = Column(DateTime(timezone=True), server_default=func.now(), comment="측정 일시")

    def __repr__(self):
        return f"<WaterQuality(ocean_id={self.ocean_id}, measured_at={self.measured_at})>"
