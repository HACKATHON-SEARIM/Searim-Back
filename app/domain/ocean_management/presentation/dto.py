from pydantic import BaseModel, Field
from typing import List


class BuildingInfo(BaseModel):
    """건물 정보 DTO"""

    building_id: int = Field(..., description="건물 ID")
    building_type: str = Field(..., description="건물 타입 (STORE/BUILDING)")
    income_rate: int = Field(..., description="초당 수익률 (크레딧/초)")

    class Config:
        json_schema_extra = {
            "example": {
                "building_id": 1,
                "building_type": "STORE",
                "income_rate": 10
            }
        }


class MyOceanResponse(BaseModel):
    """내 해양 정보 응답 DTO"""

    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    region: str = Field(..., description="시/도")
    detail: str = Field(..., description="구/군")
    current_price: int = Field(..., description="현재 가격 (1평당)")
    owned_square_meters: int = Field(..., description="소유 평수")
    buildings: List[BuildingInfo] = Field(default_factory=list, description="건물 목록")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class BuildRequest(BaseModel):
    """건물 건설 요청 DTO"""

    ocean_id: int = Field(..., description="해양 ID", gt=0)
    build_type: str = Field(..., description="건물 타입 (STORE 또는 BUILDING)")

    class Config:
        json_schema_extra = {
            "example": {
                "ocean_id": 145,
                "build_type": "STORE"
            }
        }


class BuildResponse(BaseModel):
    """건물 건설 응답 DTO"""

    message: str = Field(..., description="응답 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "음식점 또는 빌딩 생성에 성공하였습니다"
            }
        }


class PurchaseOceanRequest(BaseModel):
    """해양 구매 요청 DTO"""

    square_meters: int = Field(..., description="구매할 평수", gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "square_meters": 100
            }
        }


class PurchaseOceanResponse(BaseModel):
    """해양 구매 응답 DTO"""

    message: str = Field(..., description="응답 메시지")
    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    purchased_square_meters: int = Field(..., description="구매한 평수")
    total_owned_square_meters: int = Field(..., description="총 소유 평수")
    remaining_credits: int = Field(..., description="남은 크레딧")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "해양 구매에 성공하였습니다",
                "ocean_id": 1,
                "ocean_name": "부산 앞바다",
                "purchased_square_meters": 100,
                "total_owned_square_meters": 100,
                "remaining_credits": 8000
            }
        }
