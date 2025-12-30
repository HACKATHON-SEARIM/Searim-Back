from sqlalchemy.orm import Session
from typing import Optional, List
from app.domain.ocean.domain.entity import Ocean, WaterQuality
from app.domain.article.domain.entity import Article


class OceanRepository:
    """해양 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, ocean_id: int) -> Optional[Ocean]:
        """
        해양 ID로 해양을 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            Optional[Ocean]: 조회된 해양 객체 또는 None
        """
        return self.db.query(Ocean).filter(Ocean.ocean_id == ocean_id).first()


class WaterQualityRepository:
    """수질 데이터 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_latest_by_ocean_id(self, ocean_id: int) -> Optional[WaterQuality]:
        """
        특정 해양의 최신 수질 데이터를 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            Optional[WaterQuality]: 최신 수질 데이터 또는 None
        """
        return (
            self.db.query(WaterQuality)
            .filter(WaterQuality.ocean_id == ocean_id)
            .order_by(WaterQuality.measured_at.desc())
            .first()
        )


class ArticleRepository:
    """기사 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_by_ocean_id(self, ocean_id: int, limit: int = 10) -> List[Article]:
        """
        특정 해양의 기사 목록을 조회합니다.

        Args:
            ocean_id: 해양 ID
            limit: 조회할 기사 개수 (기본값: 10)

        Returns:
            List[Article]: 기사 목록
        """
        return (
            self.db.query(Article)
            .filter(Article.ocean_id == ocean_id)
            .order_by(Article.created_at.desc())
            .limit(limit)
            .all()
        )
