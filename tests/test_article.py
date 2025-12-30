"""
Article 도메인 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestArticle:
    """기사 API 테스트"""

    def test_get_articles_empty(self, client: TestClient):
        """기사가 없을 때 조회 테스트"""
        response = client.get("/api/article")

        assert response.status_code == 200
        data = response.json()
        assert data["oceans"] == []

    def test_get_articles_with_data(self, client: TestClient, test_ocean, db_session):
        """기사 조회 성공 테스트"""
        # 기사 생성
        from app.domain.article.domain.entity import Article, ArticleSentiment

        article = Article(
            ocean_id=test_ocean.ocean_id,
            ocean_name=test_ocean.ocean_name,
            title="테스트 기사",
            url="https://example.com/article/1",
            sentiment=ArticleSentiment.POSITIVE,
            price_change=150
        )
        db_session.add(article)
        db_session.commit()

        # 기사 조회
        response = client.get("/api/article")

        assert response.status_code == 200
        data = response.json()
        assert len(data["oceans"]) == 1
        assert data["oceans"][0]["ocean_id"] == test_ocean.ocean_id
        assert len(data["oceans"][0]["articles"]) == 1
        assert data["oceans"][0]["articles"][0]["title"] == "테스트 기사"
