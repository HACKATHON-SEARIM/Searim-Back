from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class WaterQualityResponse(BaseModel):
    """수질 데이터 응답 DTO"""

    id: int = Field(..., description="수질 데이터 ID")
    ocean_id: int = Field(..., description="해양 ID")
    dissolved_oxygen_value: Optional[float] = Field(None, description="용존산소 농도 (mg/L)")
    dissolved_oxygen_status: Optional[str] = Field(None, description="용존산소 상태")
    ph_value: Optional[float] = Field(None, description="pH 값")
    ph_status: Optional[str] = Field(None, description="pH 상태")
    nitrogen_value: Optional[float] = Field(None, description="질소 농도 (mg/L)")
    nitrogen_status: Optional[str] = Field(None, description="질소 상태")
    phosphorus_value: Optional[float] = Field(None, description="인 농도 (mg/L)")
    phosphorus_status: Optional[str] = Field(None, description="인 상태")
    turbidity_value: Optional[float] = Field(None, description="탁도 (NTU)")
    turbidity_status: Optional[str] = Field(None, description="탁도 상태")
    heavy_metals_detected: int = Field(..., description="중금속 검출 여부 (0: 미검출, 1: 검출)")
    oil_spill_detected: int = Field(..., description="유류 오염 여부 (0: 미검출, 1: 검출)")
    price_change: int = Field(..., description="수질에 따른 가격 변동")
    measured_at: datetime = Field(..., description="측정 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ocean_id": 1,
                "dissolved_oxygen_value": 8.5,
                "dissolved_oxygen_status": "normal",
                "ph_value": 8.2,
                "ph_status": "normal",
                "nitrogen_value": 0.3,
                "nitrogen_status": "normal",
                "phosphorus_value": 0.02,
                "phosphorus_status": "normal",
                "turbidity_value": 2.1,
                "turbidity_status": "normal",
                "heavy_metals_detected": 0,
                "oil_spill_detected": 0,
                "price_change": 0,
                "measured_at": "2025-12-30T12:00:00Z"
            }
        }


class ArticleResponse(BaseModel):
    """기사 응답 DTO"""

    article_id: int = Field(..., description="기사 ID")
    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    title: str = Field(..., description="기사 제목")
    url: str = Field(..., description="기사 URL")
    sentiment: str = Field(..., description="기사 감성 (positive, negative, neutral)")
    price_change: int = Field(..., description="가격 변동량")
    created_at: datetime = Field(..., description="생성 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "article_id": 1,
                "ocean_id": 1,
                "ocean_name": "동해",
                "title": "동해 해양 생태계 개선 프로젝트 성공",
                "url": "https://example.com/article/1",
                "sentiment": "positive",
                "price_change": 100,
                "created_at": "2025-12-30T12:00:00Z"
            }
        }


class PriceInfoResponse(BaseModel):
    """가격 정보 응답 DTO"""

    base_price: int = Field(..., description="기본 가격 (1평당)")
    current_price: int = Field(..., description="현재 가격 (1평당)")
    price_change_rate: float = Field(..., description="가격 변동률 (%)")

    class Config:
        json_schema_extra = {
            "example": {
                "base_price": 1000,
                "current_price": 1200,
                "price_change_rate": 20.0
            }
        }


class OceanDetailResponse(BaseModel):
    """해양 상세 정보 응답 DTO"""

    ocean_id: int = Field(..., description="해양 ID")
    ocean_name: str = Field(..., description="해양 이름")
    lat: float = Field(..., description="위도")
    lon: float = Field(..., description="경도")
    region: str = Field(..., description="시/도")
    detail: str = Field(..., description="구/군")
    total_square_meters: int = Field(..., description="총 평수")
    available_square_meters: int = Field(..., description="구매 가능한 평수")
    garbage_collection_count: int = Field(..., description="쓰레기 수집 횟수")
    price_info: PriceInfoResponse = Field(..., description="가격 정보")
    water_quality: Optional[WaterQualityResponse] = Field(None, description="최신 수질 데이터")
    articles: List[ArticleResponse] = Field(default_factory=list, description="관련 기사 목록")
    created_at: datetime = Field(..., description="생성 일시")
    updated_at: datetime = Field(..., description="수정 일시")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ocean_id": 1,
                "ocean_name": "동해",
                "lat": 37.5665,
                "lon": 126.9780,
                "region": "강원도",
                "detail": "강릉시",
                "total_square_meters": 10000,
                "available_square_meters": 8000,
                "garbage_collection_count": 15,
                "price_info": {
                    "base_price": 1000,
                    "current_price": 1200,
                    "price_change_rate": 20.0
                },
                "water_quality": {
                    "id": 1,
                    "ocean_id": 1,
                    "dissolved_oxygen_value": 8.5,
                    "dissolved_oxygen_status": "normal",
                    "ph_value": 8.2,
                    "ph_status": "normal",
                    "nitrogen_value": 0.3,
                    "nitrogen_status": "normal",
                    "phosphorus_value": 0.02,
                    "phosphorus_status": "normal",
                    "turbidity_value": 2.1,
                    "turbidity_status": "normal",
                    "heavy_metals_detected": 0,
                    "oil_spill_detected": 0,
                    "price_change": 0,
                    "measured_at": "2025-12-30T12:00:00Z"
                },
                "articles": [
                    {
                        "article_id": 1,
                        "ocean_id": 1,
                        "ocean_name": "동해",
                        "title": "동해 해양 생태계 개선 프로젝트 성공",
                        "url": "https://example.com/article/1",
                        "sentiment": "positive",
                        "price_change": 100,
                        "created_at": "2025-12-30T12:00:00Z"
                    }
                ],
                "created_at": "2025-12-30T10:00:00Z",
                "updated_at": "2025-12-30T12:00:00Z"
            }
        }
