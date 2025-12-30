"""
Ocean Trade 도메인 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestOceanTrade:
    """해양 거래 API 테스트"""

    def test_get_purchasable_oceans(self, client: TestClient, auth_headers, test_ocean):
        """구매 가능한 해양 조회 테스트"""
        response = client.get("/api/ocean/purchase", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["ocean_id"] == test_ocean.ocean_id

    def test_get_purchasable_oceans_with_filter(self, client: TestClient, auth_headers, test_ocean):
        """지역 필터로 구매 가능한 해양 조회 테스트"""
        response = client.get(
            f"/api/ocean/purchase?region={test_ocean.region}&detail={test_ocean.detail}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_purchase_ocean_success(self, client: TestClient, auth_headers, test_ocean):
        """해양 구매 성공 테스트"""
        response = client.post(
            f"/api/ocean/{test_ocean.ocean_id}/purchase",
            headers=auth_headers,
            json={"square_meters": 10}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ownership"]["ocean_id"] == test_ocean.ocean_id
        assert data["ownership"]["square_meters"] == 10

    def test_purchase_ocean_insufficient_credits(self, client: TestClient, db_session):
        """크레딧 부족으로 해양 구매 실패 테스트"""
        # 크레딧이 부족한 사용자 생성
        from app.domain.auth.domain.entity import User
        from app.global.security.password import hash_password

        poor_user = User(
            user_id="poor_user",
            password=hash_password("password"),
            credits=10  # 적은 크레딧
        )
        db_session.add(poor_user)
        db_session.commit()

        # 로그인
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)

        login_response = client.post(
            "/api/auth/login",
            json={"user_id": "poor_user", "password": "password"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 해양 생성
        from app.domain.ocean.domain.entity import Ocean
        ocean = Ocean(
            ocean_name="비싼 해양",
            lat=35.1796,
            lon=129.0756,
            region="부산광역시",
            detail="해운대구",
            base_price=10000,
            current_price=10000,
            total_square_meters=100,
            available_square_meters=100
        )
        db_session.add(ocean)
        db_session.commit()

        # 구매 시도
        response = client.post(
            f"/api/ocean/{ocean.ocean_id}/purchase",
            headers=headers,
            json={"square_meters": 10}
        )

        assert response.status_code == 400

    def test_register_sale_success(self, client: TestClient, auth_headers, test_ocean, db_session):
        """판매 등록 성공 테스트"""
        # 소유권 생성
        from app.global.security.jwt import decode_access_token
        from app.domain.ocean_management.domain.entity import OceanOwnership

        token = auth_headers["Authorization"].replace("Bearer ", "")
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        ownership = OceanOwnership(
            user_id=user_id,
            ocean_id=test_ocean.ocean_id,
            square_meters=50
        )
        db_session.add(ownership)
        db_session.commit()

        # 판매 등록
        response = client.post(
            f"/api/ocean/{test_ocean.ocean_id}/sale",
            headers=auth_headers,
            json={"square_meters": 10, "price": 1500}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ocean_id"] == test_ocean.ocean_id
        assert data["square_meters"] == 10

    def test_register_auction_success(self, client: TestClient, auth_headers, test_ocean, db_session):
        """경매 등록 성공 테스트"""
        # 소유권 생성
        from app.global.security.jwt import decode_access_token
        from app.domain.ocean_management.domain.entity import OceanOwnership

        token = auth_headers["Authorization"].replace("Bearer ", "")
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        ownership = OceanOwnership(
            user_id=user_id,
            ocean_id=test_ocean.ocean_id,
            square_meters=50
        )
        db_session.add(ownership)
        db_session.commit()

        # 경매 등록
        response = client.post(
            f"/api/ocean/{test_ocean.ocean_id}/auction",
            headers=auth_headers,
            json={"square_meters": 10}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ocean_id"] == test_ocean.ocean_id
        # 시작가는 현재 시세의 80%
        assert data["starting_price"] == int(test_ocean.current_price * 0.8)
