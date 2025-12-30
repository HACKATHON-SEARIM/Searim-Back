from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PurchaseOceanRequest(BaseModel):
    """해양 구매 요청 DTO"""

    square_meters: int = Field(..., description="구매할 평수", gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "square_meters": 100
            }
        }


class RegisterSaleRequest(BaseModel):
    """해양 판매 등록 요청 DTO"""

    square_meters: int = Field(..., description="판매할 평수", gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "square_meters": 50
            }
        }


class RegisterAuctionRequest(BaseModel):
    """경매 등록 요청 DTO"""

    square_meters: int = Field(..., description="경매에 올릴 평수", gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "square_meters": 30
            }
        }


class BidOnAuctionRequest(BaseModel):
    """경매 입찰 요청 DTO"""

    bid_amount: int = Field(..., description="입찰 금액", gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "bid_amount": 50000
            }
        }


class OceanResponse(BaseModel):
    """해양 정보 응답 DTO"""

    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    lat: float = Field(..., description="위도")
    lon: float = Field(..., description="경도")
    region: str = Field(..., description="지역")
    detail: str = Field(..., description="상세 지역")
    current_price: int = Field(..., description="현재 가격 (1평당)")
    available_square_meters: int = Field(..., description="구매 가능한 평수")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ocean_id": 1,
                "ocean_name": "부산 앞바다",
                "lat": 35.1595,
                "lon": 129.1600,
                "region": "부산광역시",
                "detail": "해운대구",
                "current_price": 1000,
                "available_square_meters": 5000
            }
        }


class OwnershipResponse(BaseModel):
    """소유권 정보 응답 DTO"""

    id: int = Field(..., description="소유권 ID")
    ocean_id: int = Field(..., description="해양 ID")
    user_id: str = Field(..., description="소유자 ID")
    square_meters: int = Field(..., description="소유 평수")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ocean_id": 1,
                "user_id": "user123",
                "square_meters": 100
            }
        }


class SaleResponse(BaseModel):
    """판매 정보 응답 DTO"""

    id: int = Field(..., description="판매 ID")
    ocean_id: int = Field(..., description="해양 ID")
    seller_id: str = Field(..., description="판매자 ID")
    square_meters: int = Field(..., description="판매 평수")
    price: int = Field(..., description="판매 가격")
    status: str = Field(..., description="판매 상태")
    created_at: datetime = Field(..., description="등록 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ocean_id": 1,
                "seller_id": "user123",
                "square_meters": 50,
                "price": 75000,
                "status": "ACTIVE",
                "created_at": "2025-12-30T12:00:00Z"
            }
        }


class AuctionResponse(BaseModel):
    """경매 정보 응답 DTO"""

    id: int = Field(..., description="경매 ID")
    ocean_id: int = Field(..., description="해양 ID")
    seller_id: str = Field(..., description="판매자 ID")
    square_meters: int = Field(..., description="경매 평수")
    starting_price: int = Field(..., description="시작 가격")
    current_price: int = Field(..., description="현재 최고 입찰가")
    status: str = Field(..., description="경매 상태")
    created_at: datetime = Field(..., description="등록 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ocean_id": 1,
                "seller_id": "user123",
                "square_meters": 30,
                "starting_price": 24000,
                "current_price": 30000,
                "status": "ACTIVE",
                "created_at": "2025-12-30T12:00:00Z"
            }
        }


class BidResponse(BaseModel):
    """입찰 정보 응답 DTO"""

    id: int = Field(..., description="입찰 ID")
    auction_id: int = Field(..., description="경매 ID")
    bidder_id: str = Field(..., description="입찰자 ID")
    bid_amount: int = Field(..., description="입찰 금액")
    created_at: datetime = Field(..., description="입찰 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "auction_id": 1,
                "bidder_id": "user456",
                "bid_amount": 35000,
                "created_at": "2025-12-30T12:00:00Z"
            }
        }


class PurchaseResponse(BaseModel):
    """구매 결과 응답 DTO"""

    message: str = Field(..., description="결과 메시지")
    ownership: OwnershipResponse = Field(..., description="소유권 정보")
    remaining_credits: int = Field(..., description="남은 크레딧")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "해양 구매에 성공하였습니다.",
                "ownership": {
                    "id": 1,
                    "ocean_id": 1,
                    "user_id": "user123",
                    "square_meters": 100
                },
                "remaining_credits": 5000
            }
        }
