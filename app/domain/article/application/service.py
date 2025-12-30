from sqlalchemy.orm import Session
from typing import List, Dict
from collections import defaultdict
from app.domain.article.domain.repository import ArticleRepository
from app.domain.article.domain.entity import Article


class ArticleService:
    """기사 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ArticleRepository(db)

    def get_articles_grouped_by_ocean(self) -> Dict[int, List[Article]]:
        """
        전체 기사 목록을 해양별로 그룹화하여 조회합니다.

        Returns:
            Dict[int, List[Article]]: 해양 ID를 키로 하는 기사 목록 딕셔너리
        """
        articles = self.repository.find_all_grouped_by_ocean()

        # 해양별로 그룹화
        grouped_articles = defaultdict(list)
        for article in articles:
            grouped_articles[article.ocean_id].append(article)

        return dict(grouped_articles)

    def get_articles_by_ocean_id(self, ocean_id: int) -> List[Article]:
        """
        특정 해양의 기사 목록을 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            List[Article]: 해당 해양의 기사 목록
        """
        return self.repository.find_by_ocean_id(ocean_id)
