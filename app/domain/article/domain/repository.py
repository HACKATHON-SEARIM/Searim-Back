from sqlalchemy.orm import Session
from typing import List
from app.domain.article.domain.entity import Article


class ArticleRepository:
    """기사 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_all_grouped_by_ocean(self) -> List[Article]:
        """
        모든 기사를 해양별로 그룹화하여 조회합니다.

        Returns:
            List[Article]: 해양별로 정렬된 전체 기사 목록
        """
        return (
            self.db.query(Article)
            .order_by(Article.ocean_id, Article.created_at.desc())
            .all()
        )

    def find_by_ocean_id(self, ocean_id: int) -> List[Article]:
        """
        특정 해양의 기사 목록을 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            List[Article]: 해당 해양의 기사 목록
        """
        return (
            self.db.query(Article)
            .filter(Article.ocean_id == ocean_id)
            .order_by(Article.created_at.desc())
            .all()
        )

    def find_by_id(self, article_id: int) -> Article:
        """
        기사 ID로 기사를 조회합니다.

        Args:
            article_id: 기사 ID

        Returns:
            Article: 조회된 기사 객체 또는 None
        """
        return self.db.query(Article).filter(Article.article_id == article_id).first()

    def create(self, article: Article) -> Article:
        """
        새로운 기사를 생성합니다.

        Args:
            article: 생성할 기사 객체

        Returns:
            Article: 생성된 기사 객체
        """
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def exists_by_url(self, url: str) -> bool:
        """
        URL로 기사 존재 여부를 확인합니다.

        Args:
            url: 기사 URL

        Returns:
            bool: 존재 여부
        """
        return self.db.query(Article).filter(Article.url == url).count() > 0
