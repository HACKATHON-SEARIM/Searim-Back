"""
Ocean 도메인 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestOcean:
    """해양 조회 API 테스트"""

    def test_get_ocean_detail_success(self, client: TestClient, test_ocean):
        """해양 상세 조회 성공 테스트"""
        response = client.get(f"/api/ocean/{test_ocean.ocean_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["ocean_id"] == test_ocean.ocean_id
        assert data["ocean_name"] == test_ocean.ocean_name
        assert data["lat"] == test_ocean.lat
        assert data["lon"] == test_ocean.lon
        assert "price_info" in data
        assert "articles" in data

    def test_get_ocean_detail_not_found(self, client: TestClient):
        """존재하지 않는 해양 조회 실패 테스트"""
        response = client.get("/api/ocean/99999")

        assert response.status_code == 404
