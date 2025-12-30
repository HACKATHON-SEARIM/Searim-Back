from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.article.application.service import ArticleService
from app.domain.article.presentation.dto import (
    ArticleListResponse,
    OceanArticlesResponse,
    ArticleResponse
)

router = APIRouter(prefix="/article", tags=["Article"])


@router.get(
    "",
    response_model=ArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="기사 리스트 조회",
    description="전체 기사 목록을 해양별로 그룹화하여 조회합니다."
)
def get_articles(
    db: Session = Depends(get_db)
) -> ArticleListResponse:
    """
    기사 리스트 조회 엔드포인트

    Args:
        db: 데이터베이스 세션

    Returns:
        ArticleListResponse: 해양별로 그룹화된 기사 목록
    """
    service = ArticleService(db)
    grouped_articles = service.get_articles_grouped_by_ocean()

    # 응답 DTO 변환
    oceans = []
    for ocean_id, articles in grouped_articles.items():
        if not articles:
            continue

        ocean_name = articles[0].ocean_name if articles else ""

        ocean_articles_response = OceanArticlesResponse(
            ocean_id=ocean_id,
            ocean_name=ocean_name,
            articles=[
                ArticleResponse(
                    article_id=article.article_id,
                    ocean_id=article.ocean_id,
                    ocean_name=article.ocean_name,
                    title=article.title,
                    url=article.url,
                    sentiment=article.sentiment,
                    price_change=article.price_change,
                    created_at=article.created_at
                )
                for article in articles
            ]
        )
        oceans.append(ocean_articles_response)

    # ocean_id 기준으로 정렬
    oceans.sort(key=lambda x: x.ocean_id)

    return ArticleListResponse(oceans=oceans)
