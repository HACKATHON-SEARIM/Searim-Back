"""
Ocean Management 도메인 테스트
"""

import pytest
from fastapi.testclient import TestClient
from app.domain.ocean_management.domain.entity import OceanOwnership, Building, BuildingType


class TestOceanManagement:
    """해양 관리 API 테스트"""

    def test_get_my_oceans_empty(self, client: TestClient, auth_headers):
        """보유 해양이 없을 때 조회 테스트"""
        response = client.get("/api/ocean/my", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_oceans_with_ownership(self, client: TestClient, auth_headers, test_ocean, db_session):
        """보유 해양 조회 성공 테스트"""
        # 회원가입한 사용자 ID 가져오기
        from app.global.security.jwt import decode_access_token
        token = auth_headers["Authorization"].replace("Bearer ", "")
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        # 소유권 생성
        ownership = OceanOwnership(
            user_id=user_id,
            ocean_id=test_ocean.ocean_id,
            square_meters=50
        )
        db_session.add(ownership)
        db_session.commit()

        response = client.get("/api/ocean/my", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ocean_id"] == test_ocean.ocean_id
        assert data[0]["owned_square_meters"] == 50

    def test_build_on_ocean_success(self, client: TestClient, auth_headers, test_ocean, db_session):
        """건물 짓기 성공 테스트"""
        # 소유권 생성
        from app.global.security.jwt import decode_access_token
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

        # 건물 짓기
        response = client.post(
            "/api/ocean/my/build",
            headers=auth_headers,
            json={"ocean_id": test_ocean.ocean_id, "build_type": "STORE"}
        )

        assert response.status_code == 201
        assert "성공" in response.json()["message"]

    def test_build_on_ocean_no_ownership(self, client: TestClient, auth_headers, test_ocean):
        """소유권 없이 건물 짓기 실패 테스트"""
        response = client.post(
            "/api/ocean/my/build",
            headers=auth_headers,
            json={"ocean_id": test_ocean.ocean_id, "build_type": "STORE"}
        )

        assert response.status_code == 403

    def test_build_on_ocean_unauthorized(self, client: TestClient, test_ocean):
        """인증 없이 건물 짓기 실패 테스트"""
        response = client.post(
            "/api/ocean/my/build",
            json={"ocean_id": test_ocean.ocean_id, "build_type": "STORE"}
        )

        assert response.status_code == 401
