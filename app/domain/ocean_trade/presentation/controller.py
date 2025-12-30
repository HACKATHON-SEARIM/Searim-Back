from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.domain.ocean_trade.application.service import OceanTradeService
from app.domain.ocean_trade.presentation.dto import (
    PurchaseOceanRequest,
    RegisterSaleRequest,
    RegisterAuctionRequest,
    BidOnAuctionRequest,
    OceanResponse,
    OwnershipResponse,
    SaleResponse,
    AuctionResponse,
    BidResponse,
    PurchaseResponse
)
from app.core.security.jwt import get_current_username
from app.domain.auth.domain.repository import UserRepository

router = APIRouter(prefix="/ocean-trade", tags=["Ocean Trade"])


@router.get(
    "/purchase",
    response_model=List[OceanResponse],
    status_code=status.HTTP_200_OK,
    summary="구매 가능한 해양 목록 조회",
    description="구매 가능한 해양 목록을 조회합니다. 지역(region) 및 세부 지역(detail)으로 필터링할 수 있습니다."
)
def get_purchasable_oceans(
    region: Optional[str] = Query(None, description="지역 필터 (시/도)"),
    detail: Optional[str] = Query(None, description="세부 지역 필터 (시/군/구)"),
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> List[OceanResponse]:
    """
    구매 가능한 해양 목록 조회 엔드포인트

    Args:
        region: 지역 필터 (시/도)
        detail: 세부 지역 필터 (시/군/구)
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        List[OceanResponse]: 구매 가능한 해양 목록
    """
    service = OceanTradeService(db)
    oceans = service.get_purchasable_oceans(region=region, detail=detail)
    return [OceanResponse.model_validate(ocean) for ocean in oceans]


@router.post(
    "/{ocean_id}/purchase",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="해양 구매",
    description="특정 해양을 구매합니다. 구매 시 크레딧이 차감되고 소유권이 생성됩니다."
)
def purchase_ocean(
    ocean_id: int,
    request: PurchaseOceanRequest,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> PurchaseResponse:
    """
    해양 구매 엔드포인트

    Args:
        ocean_id: 해양 ID
        request: 구매 요청 (면적)
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        PurchaseResponse: 구매 결과 및 소유권 정보

    Raises:
        HTTPException 404: 해양을 찾을 수 없는 경우
        HTTPException 400: 구매 가능한 면적이 부족하거나 크레딧이 부족한 경우
    """
    service = OceanTradeService(db)
    ownership = service.purchase_ocean(
        ocean_id=ocean_id,
        username=current_username,
        square_meters=request.square_meters
    )

    # 사용자 크레딧 조회
    user_repository = UserRepository(db)
    user = user_repository.find_by_username(current_username)

    return PurchaseResponse(
        message="해양 구매에 성공하였습니다.",
        ownership=OwnershipResponse.model_validate(ownership),
        remaining_credits=user.credits
    )


@router.post(
    "/{ocean_id}/sale",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="해양 판매 등록",
    description="소유한 해양을 판매 등록합니다. 판매 등록 시 크레딧이 소모됩니다."
)
def register_sale(
    ocean_id: int,
    request: RegisterSaleRequest,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> SaleResponse:
    """
    해양 판매 등록 엔드포인트

    Args:
        ocean_id: 해양 ID
        request: 판매 요청 (면적, 가격)
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        SaleResponse: 등록된 판매 정보

    Raises:
        HTTPException 404: 해양을 찾을 수 없는 경우
        HTTPException 400: 소유권이 부족한 경우
    """
    service = OceanTradeService(db)
    sale = service.register_sale(
        ocean_id=ocean_id,
        seller_username=current_username,
        square_meters=request.square_meters,
        price=request.price
    )
    return SaleResponse.model_validate(sale)


@router.post(
    "/{ocean_id}/auction",
    response_model=AuctionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="해양 경매 등록",
    description="소유한 해양을 경매에 등록합니다. 시작가는 현재 시세의 80%로 자동 설정됩니다."
)
def register_auction(
    ocean_id: int,
    request: RegisterAuctionRequest,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> AuctionResponse:
    """
    해양 경매 등록 엔드포인트

    Args:
        ocean_id: 해양 ID
        request: 경매 요청 (면적)
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        AuctionResponse: 등록된 경매 정보

    Raises:
        HTTPException 404: 해양을 찾을 수 없는 경우
        HTTPException 400: 소유권이 부족한 경우
    """
    service = OceanTradeService(db)
    auction = service.register_auction(
        ocean_id=ocean_id,
        seller_username=current_username,
        square_meters=request.square_meters
    )
    return AuctionResponse.model_validate(auction)


@router.post(
    "/sale/{sale_id}/purchase",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="판매 등록된 해양 구매",
    description="등록된 판매 해양을 구매합니다. 크레딧이 차감되고 해양 소유권이 이전됩니다."
)
def purchase_from_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> PurchaseResponse:
    """
    판매 등록된 해양 구매 엔드포인트

    Args:
        sale_id: 판매 ID
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        PurchaseResponse: 구매 결과 및 소유권 정보

    Raises:
        HTTPException 404: 판매를 찾을 수 없는 경우
        HTTPException 400: 해양 소유자와 동일하거나 크레딧이 부족한 경우
    """
    service = OceanTradeService(db)
    ownership, sale = service.purchase_from_sale(
        sale_id=sale_id,
        buyer_username=current_username
    )

    # 사용자 크레딧 조회
    user_repository = UserRepository(db)
    user = user_repository.find_by_username(current_username)

    return PurchaseResponse(
        message="판매 등록된 해양 구매에 성공하였습니다.",
        ownership=OwnershipResponse.model_validate(ownership),
        remaining_credits=user.credits
    )


@router.post(
    "/auction/{auction_id}/bid",
    response_model=BidResponse,
    status_code=status.HTTP_201_CREATED,
    summary="경매 입찰",
    description="진행 중인 경매에 입찰합니다. 입찰 금액은 현재 최고가보다 높아야 합니다."
)
def bid_on_auction(
    auction_id: int,
    request: BidOnAuctionRequest,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> BidResponse:
    """
    경매 입찰 엔드포인트

    Args:
        auction_id: 경매 ID
        request: 입찰 요청 (입찰 금액)
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        BidResponse: 입찰 정보

    Raises:
        HTTPException 404: 경매를 찾을 수 없는 경우
        HTTPException 400: 경매가 종료되었거나 입찰 금액이 최고가보다 낮은 경우
    """
    service = OceanTradeService(db)
    bid = service.bid_on_auction(
        auction_id=auction_id,
        bidder_username=current_username,
        bid_amount=request.bid_amount
    )
    return BidResponse.model_validate(bid)


@router.post(
    "/auction/{auction_id}/finalize",
    response_model=PurchaseResponse,
    status_code=status.HTTP_200_OK,
    summary="경매 종료",
    description="경매를 종료하고 최고 입찰자에게 소유권을 이전합니다. (판매자만 호출 가능)"
)
def finalize_auction(
    auction_id: int,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username)
) -> PurchaseResponse:
    """
    경매 종료 엔드포인트

    Args:
        auction_id: 경매 ID
        db: 데이터베이스 세션
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)

    Returns:
        PurchaseResponse: 입찰 결과 및 소유권 정보

    Raises:
        HTTPException 404: 경매를 찾을 수 없는 경우
        HTTPException 400: 경매가 이미 종료되었거나 입찰이 없는 경우
    """
    service = OceanTradeService(db)
    ownership, auction = service.finalize_auction(auction_id=auction_id)

    # 입찰자의 사용자 크레딧 조회
    user_repository = UserRepository(db)
    user = user_repository.find_by_username(ownership.user_id)

    return PurchaseResponse(
        message="경매가 종료되었습니다.",
        ownership=OwnershipResponse.model_validate(ownership),
        remaining_credits=user.credits
    )
