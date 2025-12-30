from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.domain.ocean.application.service import OceanService
from app.domain.ocean.presentation.dto import (
    OceanDetailResponse,
    OceanListItemResponse,
    PriceInfoResponse,
    WaterQualityResponse,
    ArticleResponse
)

router = APIRouter(prefix="/ocean", tags=["Ocean"])


@router.get(
    "",
    response_model=List[OceanListItemResponse],
    status_code=status.HTTP_200_OK,
    summary="해양 목록 조회",
    description="해양 목록을 조회합니다. 지역(region) 및 세부 지역(detail)으로 필터링할 수 있습니다."
)
def get_oceans(
    region: Optional[str] = Query(None, description="지역 필터 (시/도)"),
    detail: Optional[str] = Query(None, description="세부 지역 필터 (시/군/구)"),
    db: Session = Depends(get_db)
) -> List[OceanListItemResponse]:
    """
    해양 목록 조회 엔드포인트

    Args:
        region: 지역 필터 (시/도)
        detail: 세부 지역 필터 (시/군/구)
        db: 데이터베이스 세션

    Returns:
        List[OceanListItemResponse]: 해양 목록
    """
    service = OceanService(db)
    oceans = service.get_all_oceans(region=region, detail=detail)

    return [
        OceanListItemResponse(
            ocean_id=ocean.ocean_id,
            ocean_name=ocean.ocean_name,
            lat=ocean.lat,
            lon=ocean.lon,
            region=ocean.region,
            detail=ocean.detail,
            current_price=ocean.current_price,
            available_square_meters=ocean.available_square_meters
        )
        for ocean in oceans
    ]


@router.get(
    "/{ocean_id}",
    response_model=OceanDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="해양 상세 조회",
    description="해양의 상세 정보를 조회합니다. 해양 정보, 최신 수질 데이터, 관련 기사 목록, 가격 정보, 쓰레기 수집 횟수를 포함합니다."
)
def get_ocean_detail(
    ocean_id: int,
    db: Session = Depends(get_db)
) -> OceanDetailResponse:
    """
    해양 상세 조회 엔드포인트

    Args:
        ocean_id: 해양 ID
        db: 데이터베이스 세션

    Returns:
        OceanDetailResponse: 해양 상세 정보

    Raises:
        HTTPException 404: 해양이 존재하지 않는 경우
    """
    service = OceanService(db)
    ocean, water_quality, articles = service.get_ocean_detail(ocean_id)

    # 가격 변동률 계산
    price_change_rate = 0.0
    if ocean.base_price > 0:
        price_change_rate = ((ocean.current_price - ocean.base_price) / ocean.base_price) * 100

    # PriceInfoResponse 생성
    price_info = PriceInfoResponse(
        base_price=ocean.base_price,
        current_price=ocean.current_price,
        price_change_rate=round(price_change_rate, 2)
    )

    # WaterQualityResponse 생성 (있는 경우)
    water_quality_response = None
    if water_quality:
        water_quality_response = WaterQualityResponse.model_validate(water_quality)

    # ArticleResponse 리스트 생성
    article_responses = [
        ArticleResponse.model_validate(article)
        for article in articles
    ]

    # OceanDetailResponse 생성
    return OceanDetailResponse(
        ocean_id=ocean.ocean_id,
        ocean_name=ocean.ocean_name,
        lat=ocean.lat,
        lon=ocean.lon,
        region=ocean.region,
        detail=ocean.detail,
        total_square_meters=ocean.total_square_meters,
        available_square_meters=ocean.available_square_meters,
        garbage_collection_count=ocean.garbage_collection_count,
        price_info=price_info,
        water_quality=water_quality_response,
        articles=article_responses,
        created_at=ocean.created_at,
        updated_at=ocean.updated_at
    )
