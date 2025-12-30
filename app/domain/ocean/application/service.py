from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.domain.ocean.domain.repository import (
    OceanRepository,
    WaterQualityRepository,
    ArticleRepository
)
from app.domain.ocean.domain.entity import Ocean, WaterQuality
from app.domain.article.domain.entity import Article
from typing import Optional, List, Tuple


class OceanService:
    """해양 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.ocean_repository = OceanRepository(db)
        self.water_quality_repository = WaterQualityRepository(db)
        self.article_repository = ArticleRepository(db)

    def get_all_oceans(
        self,
        region: Optional[str] = None,
        detail: Optional[str] = None
    ) -> List[Ocean]:
        """
        해양 목록을 조회합니다.

        Args:
            region: 지역 필터 (시/도)
            detail: 세부 지역 필터 (시/군/구)

        Returns:
            List[Ocean]: 해양 목록
        """
        return self.ocean_repository.find_all(region=region, detail=detail)

    def get_ocean_detail(
        self,
        ocean_id: int
    ) -> Tuple[Ocean, Optional[WaterQuality], List[Article]]:
        """
        해양 상세 정보를 조회합니다.
        해양 정보, 최신 수질 데이터, 기사 목록을 포함합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            Tuple[Ocean, Optional[WaterQuality], List[Article]]:
                (해양 정보, 수질 데이터, 기사 목록)

        Raises:
            HTTPException 404: 해양이 존재하지 않는 경우
        """
        # 해양 조회
        ocean = self.ocean_repository.find_by_id(ocean_id)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해양 ID {ocean_id}를 찾을 수 없습니다."
            )

        # 최신 수질 데이터 조회
        water_quality = self.water_quality_repository.find_latest_by_ocean_id(ocean_id)

        # 기사 목록 조회 (최신 10개)
        articles = self.article_repository.find_by_ocean_id(ocean_id, limit=10)

        return ocean, water_quality, articles
