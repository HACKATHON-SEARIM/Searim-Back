from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.domain.ocean_management.application.service import OceanManagementService
from app.domain.ocean_management.presentation.dto import (
    MyOceanResponse,
    BuildRequest,
    BuildResponse
)
from app.core.security.jwt import get_current_user_id

router = APIRouter(prefix="/my-ocean", tags=["Ocean Management"])


@router.get(
    "",
    response_model=List[MyOceanResponse],
    status_code=status.HTTP_200_OK,
    summary="내 해양 지역 조회",
    description="사용자가 소유한 해양 목록과 건물 정보를 조회합니다. JWT 인증이 필요합니다."
)
def get_my_oceans(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> List[MyOceanResponse]:
    """
    내 해양 지역 조회 엔드포인트

    Args:
        current_user_id: 현재 로그인한 사용자 ID (JWT에서 추출)
        db: 데이터베이스 세션

    Returns:
        List[MyOceanResponse]: 소유 해양 목록 및 건물 정보

    Example Response:
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
    service = OceanManagementService(db)
    oceans = service.get_my_oceans(current_user_id)
    return oceans


@router.post(
    "/build",
    response_model=BuildResponse,
    status_code=status.HTTP_201_CREATED,
    summary="건물 짓기",
    description="소유한 해양에 건물(음식점 또는 빌딩)을 건설합니다. JWT 인증이 필요합니다."
)
def build_on_ocean(
    request: BuildRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> BuildResponse:
    """
    건물 짓기 엔드포인트

    Args:
        request: 건물 건설 요청 (ocean_id, build_type)
        current_user_id: 현재 로그인한 사용자 ID (JWT에서 추출)
        db: 데이터베이스 세션

    Returns:
        BuildResponse: 성공 메시지

    Raises:
        HTTPException 400: 잘못된 건물 타입
        HTTPException 403: 해양 소유권이 없는 경우
        HTTPException 404: 해양이 존재하지 않는 경우

    Example Request:
        {
            "ocean_id": 145,
            "build_type": "STORE"
        }

    Example Response:
        {
            "message": "음식점 또는 빌딩 생성에 성공하였습니다"
        }
    """
    service = OceanManagementService(db)
    result = service.build_on_ocean(
        user_id=current_user_id,
        ocean_id=request.ocean_id,
        build_type=request.build_type
    )
    return BuildResponse(**result)
