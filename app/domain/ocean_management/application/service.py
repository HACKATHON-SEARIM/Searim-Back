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
            # 평수가 0인 해양은 제외
            if ownership.square_meters <= 0:
                continue

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

        # 사용자 크레딧 확인
        user = self.repository.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        # 건물 타입에 따른 비용 및 수익률 설정
        if building_type == BuildingType.STORE:
            building_cost = settings.STORE_COST
            income_rate = settings.STORE_INCOME_RATE
        else:  # BuildingType.BUILDING
            building_cost = settings.BUILDING_COST
            income_rate = settings.BUILDING_INCOME_RATE

        # 크레딧 확인
        if user.credits < building_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"크레딧이 부족합니다. (필요: {building_cost}, 보유: {user.credits})"
            )

        # 크레딧 차감
        self.repository.update_user_credits(user_id, user.credits - building_cost)

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

    def purchase_ocean(self, user_id: str, ocean_id: int, square_meters: int) -> Dict[str, Any]:
        """
        해양을 구매합니다.

        Args:
            user_id: 사용자 ID
            ocean_id: 해양 ID
            square_meters: 구매할 평수

        Returns:
            Dict[str, Any]: 구매 결과

        Raises:
            HTTPException 404: 해양이 존재하지 않음
            HTTPException 400: 구매 가능한 평수 부족 또는 크레딧 부족
        """
        # 해양 존재 여부 확인
        ocean = self.repository.find_ocean_by_id(ocean_id)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해양 ID {ocean_id}가 존재하지 않습니다."
            )

        # 구매 가능한 평수 확인
        if ocean.available_square_meters < square_meters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"구매 가능한 평수가 부족합니다. (가능: {ocean.available_square_meters}평)"
            )

        # 구매 비용 계산
        total_cost = ocean.current_price * square_meters

        # 사용자 크레딧 확인 및 차감
        user = self.repository.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        if user.credits < total_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"크레딧이 부족합니다. (필요: {total_cost}, 보유: {user.credits})"
            )

        # 크레딧 차감
        self.repository.update_user_credits(user_id, user.credits - total_cost)

        # 해양 가용 평수 업데이트
        self.repository.update_ocean_available_square_meters(
            ocean_id,
            ocean.available_square_meters - square_meters
        )

        # 소유권 생성 또는 업데이트
        ownership = self.repository.find_ownership_by_user_and_ocean(user_id, ocean_id)
        if ownership:
            # 기존 소유권 업데이트
            self.repository.update_ownership_square_meters(
                ownership.id,
                ownership.square_meters + square_meters
            )
            total_owned = ownership.square_meters + square_meters
        else:
            # 새 소유권 생성
            ownership = self.repository.create_ownership(
                user_id=user_id,
                ocean_id=ocean_id,
                square_meters=square_meters
            )
            total_owned = square_meters

        return {
            "message": "해양 구매에 성공하였습니다",
            "ocean_id": ocean.ocean_id,
            "ocean_name": ocean.ocean_name,
            "purchased_square_meters": square_meters,
            "total_owned_square_meters": total_owned,
            "remaining_credits": user.credits - total_cost
        }
