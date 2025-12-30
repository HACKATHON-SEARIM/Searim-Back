from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_
from app.domain.ocean_management.domain.entity import OceanOwnership, Building, BuildingType
from app.domain.ocean.domain.entity import Ocean
from app.domain.auth.domain.entity import User


class OceanManagementRepository:
    """해양 관리 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_ownerships_by_user_id(self, user_id: str) -> List[OceanOwnership]:
        """
        사용자가 소유한 모든 해양 소유권을 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            List[OceanOwnership]: 해양 소유권 목록
        """
        return self.db.query(OceanOwnership).filter(
            OceanOwnership.user_id == user_id
        ).all()

    def find_ocean_by_id(self, ocean_id: int) -> Optional[Ocean]:
        """
        해양 ID로 해양을 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            Optional[Ocean]: 조회된 해양 객체 또는 None
        """
        return self.db.query(Ocean).filter(Ocean.ocean_id == ocean_id).first()

    def find_buildings_by_ocean_id(self, ocean_id: int) -> List[Building]:
        """
        특정 해양에 건설된 모든 건물을 조회합니다.

        Args:
            ocean_id: 해양 ID

        Returns:
            List[Building]: 건물 목록
        """
        return self.db.query(Building).filter(Building.ocean_id == ocean_id).all()

    def find_ownership_by_user_and_ocean(
        self, user_id: str, ocean_id: int
    ) -> Optional[OceanOwnership]:
        """
        사용자와 해양 ID로 소유권을 조회합니다.

        Args:
            user_id: 사용자 ID
            ocean_id: 해양 ID

        Returns:
            Optional[OceanOwnership]: 소유권 객체 또는 None
        """
        return self.db.query(OceanOwnership).filter(
            and_(
                OceanOwnership.user_id == user_id,
                OceanOwnership.ocean_id == ocean_id
            )
        ).first()

    def find_buildings_by_user_and_ocean(
        self, user_id: str, ocean_id: int
    ) -> List[Building]:
        """
        특정 사용자가 특정 해양에 건설한 모든 건물을 조회합니다.

        Args:
            user_id: 사용자 ID
            ocean_id: 해양 ID

        Returns:
            List[Building]: 건물 목록
        """
        return self.db.query(Building).filter(
            and_(
                Building.user_id == user_id,
                Building.ocean_id == ocean_id
            )
        ).all()

    def create_building(
        self, ocean_id: int, user_id: str, building_type: BuildingType, income_rate: int
    ) -> Building:
        """
        새로운 건물을 생성합니다.

        Args:
            ocean_id: 해양 ID
            user_id: 소유자 ID
            building_type: 건물 타입 (STORE/BUILDING)
            income_rate: 초당 수익률

        Returns:
            Building: 생성된 건물 객체
        """
        building = Building(
            ocean_id=ocean_id,
            user_id=user_id,
            building_type=building_type,
            income_rate=income_rate
        )
        self.db.add(building)
        self.db.commit()
        self.db.refresh(building)
        return building

    def find_user_by_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[User]: 조회된 사용자 객체 또는 None
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

    def update_user_credits(self, user_id: str, credits: int) -> User:
        """
        사용자의 크레딧을 업데이트합니다.

        Args:
            user_id: 사용자 ID
            credits: 새로운 크레딧 금액

        Returns:
            User: 업데이트된 사용자 객체
        """
        user = self.find_user_by_id(user_id)
        if user:
            user.credits = credits
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_ocean_available_square_meters(self, ocean_id: int, available_square_meters: int) -> Ocean:
        """
        해양의 구매 가능한 평수를 업데이트합니다.

        Args:
            ocean_id: 해양 ID
            available_square_meters: 새로운 구매 가능 평수

        Returns:
            Ocean: 업데이트된 해양 객체
        """
        ocean = self.find_ocean_by_id(ocean_id)
        if ocean:
            ocean.available_square_meters = available_square_meters
            self.db.commit()
            self.db.refresh(ocean)
        return ocean

    def create_ownership(self, user_id: str, ocean_id: int, square_meters: int) -> OceanOwnership:
        """
        새로운 해양 소유권을 생성합니다.

        Args:
            user_id: 사용자 ID
            ocean_id: 해양 ID
            square_meters: 소유 평수

        Returns:
            OceanOwnership: 생성된 소유권 객체
        """
        ownership = OceanOwnership(
            user_id=user_id,
            ocean_id=ocean_id,
            square_meters=square_meters
        )
        self.db.add(ownership)
        self.db.commit()
        self.db.refresh(ownership)
        return ownership

    def update_ownership_square_meters(self, ownership_id: int, square_meters: int) -> OceanOwnership:
        """
        기존 소유권의 평수를 업데이트합니다.

        Args:
            ownership_id: 소유권 ID
            square_meters: 새로운 소유 평수

        Returns:
            OceanOwnership: 업데이트된 소유권 객체
        """
        ownership = self.db.query(OceanOwnership).filter(OceanOwnership.id == ownership_id).first()
        if ownership:
            ownership.square_meters = square_meters
            self.db.commit()
            self.db.refresh(ownership)
        return ownership
