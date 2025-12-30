from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any
from app.domain.ocean_management.domain.repository import OceanManagementRepository
from app.domain.ocean_management.domain.entity import BuildingType
from app.config import get_settings

settings = get_settings()


class OceanManagementService:
    """해양 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = OceanManagementRepository(db)

    def get_my_oceans(self, user_id: str) -> List[Dict[str, Any]]:
        """
        사용자가 소유한 해양 목록과 건물 정보를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            List[Dict[str, Any]]: 소유 해양 목록 및 건물 정보

        Response Structure:
            [
                {
                    "ocean_id": 145,
                    "ocean_name": "제주 앞바다",
                    "region": "제주특별자치도",
                    "detail": "제주시",
                    "current_price": 1500,
                    "owned_square_meters": 50,
                    "buildings": [
                        {
                            "building_id": 1,
                            "building_type": "STORE",
                            "income_rate": 10
                        }
                    ]
                }
            ]
        """
        # 사용자 소유 해양 조회
        ownerships = self.repository.find_ownerships_by_user_id(user_id)

        result = []
        for ownership in ownerships:
            ocean = self.repository.find_ocean_by_id(ownership.ocean_id)
            if not ocean:
                continue

            # 해양에 건설된 건물 조회
            buildings = self.repository.find_buildings_by_user_and_ocean(
                user_id, ocean.ocean_id
            )

            ocean_data = {
                "ocean_id": ocean.ocean_id,
                "ocean_name": ocean.ocean_name,
                "region": ocean.region,
                "detail": ocean.detail,
                "current_price": ocean.current_price,
                "owned_square_meters": ownership.square_meters,
                "buildings": [
                    {
                        "building_id": building.id,
                        "building_type": building.building_type.value,
                        "income_rate": building.income_rate
                    }
                    for building in buildings
                ]
            }
            result.append(ocean_data)

        return result

    def build_on_ocean(self, user_id: str, ocean_id: int, build_type: str) -> Dict[str, str]:
        """
        해양에 건물을 짓습니다 (음식점 또는 빌딩).

        Args:
            user_id: 사용자 ID
            ocean_id: 해양 ID
            build_type: 건물 타입 ("STORE" 또는 "BUILDING")

        Returns:
            Dict[str, str]: 성공 메시지

        Raises:
            HTTPException 400: 잘못된 건물 타입
            HTTPException 403: 해양 소유권 없음
            HTTPException 404: 해양이 존재하지 않음
        """
        # 건물 타입 검증
        try:
            building_type = BuildingType(build_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"잘못된 건물 타입입니다. STORE 또는 BUILDING을 입력해주세요."
            )

        # 해양 존재 여부 확인
        ocean = self.repository.find_ocean_by_id(ocean_id)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해양 ID {ocean_id}가 존재하지 않습니다."
            )

        # 소유권 확인
        ownership = self.repository.find_ownership_by_user_and_ocean(user_id, ocean_id)
        if not ownership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"해양 ID {ocean_id}에 대한 소유권이 없습니다."
            )

        # 건물 타입에 따른 수익률 설정
        if building_type == BuildingType.STORE:
            income_rate = settings.STORE_INCOME_RATE
        else:  # BuildingType.BUILDING
            income_rate = settings.BUILDING_INCOME_RATE

        # 건물 생성
        building = self.repository.create_building(
            ocean_id=ocean_id,
            user_id=user_id,
            building_type=building_type,
            income_rate=income_rate
        )

        return {
            "message": "음식점 또는 빌딩 생성에 성공하였습니다"
        }
