from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from app.domain.article.domain.entity import ArticleSentiment


class ArticleResponse(BaseModel):
    """기사 응답 DTO"""

    article_id: int = Field(..., description="기사 ID")
    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    title: str = Field(..., description="기사 제목")
    # content: str | None = Field(None, description="기사 내용 (요약)")  # 임시 제거
    url: str = Field(..., description="기사 URL")
    image_url: str | None = Field(None, description="기사 이미지 URL")
    sentiment: ArticleSentiment = Field(..., description="기사 감성 (positive/negative/neutral)")
    price_change: int = Field(..., description="가격 변동량")
    created_at: datetime = Field(..., description="생성 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "article_id": 1,
                "ocean_id": 5,
                "ocean_name": "태안해수욕장",
                "title": "태안해수욕장, 수질 개선으로 관광객 증가",
                "url": "https://example.com/article/1",
                "sentiment": "positive",
                "price_change": 500,
                "created_at": "2025-12-30T10:00:00"
            }
        }


class OceanArticlesResponse(BaseModel):
    """해양별 기사 목록 응답 DTO"""

    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    articles: List[ArticleResponse] = Field(..., description="기사 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "ocean_id": 5,
                "ocean_name": "태안해수욕장",
                "articles": [
                    {
                        "article_id": 1,
                        "ocean_id": 5,
                        "ocean_name": "태안해수욕장",
                        "title": "태안해수욕장, 수질 개선으로 관광객 증가",
                        "url": "https://example.com/article/1",
                        "sentiment": "positive",
                        "price_change": 500,
                        "created_at": "2025-12-30T10:00:00"
                    }
                ]
            }
        }


class ArticleListResponse(BaseModel):
    """기사 리스트 응답 DTO (해양별 그룹화)"""

    oceans: List[OceanArticlesResponse] = Field(..., description="해양별 기사 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "oceans": [
                    {
                        "ocean_id": 5,
                        "ocean_name": "태안해수욕장",
                        "articles": [
                            {
                                "article_id": 1,
                                "ocean_id": 5,
                                "ocean_name": "태안해수욕장",
                                "title": "태안해수욕장, 수질 개선으로 관광객 증가",
                                "url": "https://example.com/article/1",
                                "sentiment": "positive",
                                "price_change": 500,
                                "created_at": "2025-12-30T10:00:00"
                            }
                        ]
                    },
                    {
                        "ocean_id": 7,
                        "ocean_name": "부산 해운대해수욕장",
                        "articles": [
                            {
                                "article_id": 2,
                                "ocean_id": 7,
                                "ocean_name": "부산 해운대해수욕장",
                                "title": "해운대해수욕장 해양 쓰레기 문제 심각",
                                "url": "https://example.com/article/2",
                                "sentiment": "negative",
                                "price_change": -300,
                                "created_at": "2025-12-30T09:30:00"
                            }
                        ]
                    }
                ]
            }
        }
