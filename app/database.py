from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.config import get_settings

settings = get_settings()

# MySQL 연결을 위한 추가 인자
connect_args = {}

# MySQL 전용 엔진 설정
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 검사
    pool_recycle=3600,  # 1시간마다 연결 재생성 (MySQL 8시간 timeout 방지)
    pool_size=10,  # 연결 풀 크기
    max_overflow=20,  # 최대 추가 연결 수
    echo=False,  # SQL 쿼리 로깅 (프로덕션: False, 개발: True)
    connect_args=connect_args
)

# SessionLocal 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성

    FastAPI의 Depends에서 사용됩니다.
    요청이 끝나면 자동으로 세션을 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화

    모든 테이블을 생성합니다.
    MySQL의 경우 utf8mb4 문자셋을 사용합니다.
    """
    # 모든 Entity import (테이블 생성을 위해 필요)
    from app.domain.auth.domain.entity import User
    from app.domain.ocean.domain.entity import Ocean, WaterQuality, OceanPriceHistory
    from app.domain.ocean_management.domain.entity import OceanOwnership, Building
    from app.domain.ocean_trade.domain.entity import OceanSale, OceanAuction, AuctionBid
    from app.domain.mission.domain.entity import Mission, UserMission, GarbageCollection
    from app.domain.article.domain.entity import Article

    # 테이블 생성
    Base.metadata.create_all(bind=engine)
