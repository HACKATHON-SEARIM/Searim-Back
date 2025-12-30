"""
Mission 도메인 테스트
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image


class TestMission:
    """미션 API 테스트"""

    def test_get_missions(self, client: TestClient, auth_headers, db_session):
        """미션 목록 조회 테스트"""
        # 미션 생성
        from app.domain.mission.domain.entity import Mission, MissionType

        mission = Mission(
            todo="테스트 미션",
            credits=500,
            mission_type=MissionType.DAILY
        )
        db_session.add(mission)
        db_session.commit()

        # 미션 조회
        response = client.get("/api/mission", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["todo"] == "테스트 미션"
        assert data[0]["credits"] == 500
        assert data[0]["completed"] == 0

    def test_get_missions_unauthorized(self, client: TestClient):
        """인증 없이 미션 조회 실패 테스트"""
        response = client.get("/api/mission")

        assert response.status_code == 401

    def test_complete_mission_unauthorized(self, client: TestClient):
        """인증 없이 미션 완료 실패 테스트"""
        # 테스트 이미지 생성
        image = Image.new('RGB', (100, 100), color='blue')
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        response = client.post(
            "/api/mission/1",
            files={"image": ("test.png", img_byte_arr, "image/png")}
        )

        assert response.status_code == 401
