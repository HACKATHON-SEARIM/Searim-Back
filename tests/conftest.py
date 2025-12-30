"""
Pytest 설정 및 공통 픽스처
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.domain.auth.domain.entity import User
from app.domain.ocean.domain.entity import Ocean
from app.global.security.password import hash_password

# 테스트용 인메모리 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """테스트용 데이터베이스 세션"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """각 테스트마다 새로운 데이터베이스 세션을 생성"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """테스트 클라이언트"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db_session):
    """테스트용 사용자 생성"""
    user = User(
        user_id="test_user",
        password=hash_password("test_password"),
        credits=10000
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client):
    """인증 헤더 생성 (로그인 후 토큰 발급)"""
    # 회원가입
    response = client.post(
        "/api/auth/signup",
        json={"user_id": "auth_test_user", "password": "test_password"}
    )
    assert response.status_code == 201

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_ocean(db_session):
    """테스트용 해양 생성"""
    ocean = Ocean(
        ocean_name="테스트 해양",
        lat=35.1796,
        lon=129.0756,
        region="부산광역시",
        detail="해운대구",
        base_price=1000,
        current_price=1200,
        total_square_meters=100,
        available_square_meters=100,
        garbage_collection_count=0
    )
    db_session.add(ocean)
    db_session.commit()
    db_session.refresh(ocean)
    return ocean
