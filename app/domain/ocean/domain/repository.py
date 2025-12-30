from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from app.domain.ocean.domain.entity import Ocean, WaterQuality, OceanPriceHistory
from app.domain.article.domain.entity import Article


class OceanRepository:
    """해양 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_all(
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
        query = self.db.query(Ocean)

        if region:
            query = query.filter(Ocean.region == region)
        if detail:
            query = query.filter(Ocean.detail == detail)

        return query.all()

    def find_by_id(self, ocean_id: int) -> Optional[Ocean]:
        """
        해양 ID로 해양을 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            Optional[Ocean]: 조회된 해양 객체 또는 None
        """
        return self.db.query(Ocean).filter(Ocean.ocean_id == ocean_id).first()

    def add_price_history(self, ocean_id: int, price: int, limit: int = 10) -> None:
        """
        해양 시세 이력을 추가하고 최근 limit개만 유지합니다.

        Args:
            ocean_id: 해양 ID
            price: 시세 (1평당)
            limit: 유지할 이력 개수
        """
        history = OceanPriceHistory(ocean_id=ocean_id, price=price)
        self.db.add(history)
        self.db.flush()

        extra_ids = (
            self.db.query(OceanPriceHistory.id)
            .filter(OceanPriceHistory.ocean_id == ocean_id)
            .order_by(
                OceanPriceHistory.recorded_at.desc(),
                OceanPriceHistory.id.desc()
            )
            .offset(limit)
            .all()
        )
        if extra_ids:
            self.db.query(OceanPriceHistory).filter(
                OceanPriceHistory.id.in_([row.id for row in extra_ids])
            ).delete(synchronize_session=False)

    def find_recent_prices_by_ocean_ids(
        self,
        ocean_ids: List[int],
        limit: int = 10
    ) -> Dict[int, List[int]]:
        """
        해양별 최근 시세 목록을 조회합니다.

        Args:
            ocean_ids: 해양 ID 목록
            limit: 각 해양별 반환할 최근 시세 개수

        Returns:
            Dict[int, List[int]]: 해양 ID별 시세 리스트 (최신순)
        """
        if not ocean_ids:
            return {}

        histories = (
            self.db.query(OceanPriceHistory)
            .filter(OceanPriceHistory.ocean_id.in_(ocean_ids))
            .order_by(
                OceanPriceHistory.ocean_id,
                OceanPriceHistory.recorded_at.desc(),
                OceanPriceHistory.id.desc()
            )
            .all()
        )

        result: Dict[int, List[int]] = {ocean_id: [] for ocean_id in ocean_ids}
        for history in histories:
            prices = result.setdefault(history.ocean_id, [])
            if len(prices) < limit:
                prices.append(history.price)

        return result


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
