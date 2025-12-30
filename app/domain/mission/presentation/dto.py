from pydantic import BaseModel, Field
from typing import List


class MissionResponse(BaseModel):
    """미션 응답 DTO"""

    todo_id: int = Field(..., description="미션 ID")
    todo: str = Field(..., description="미션 내용")
    credits: int = Field(..., description="보상 크레딧")
    mission_type: str = Field(..., description="미션 타입 (DAILY, SPECIAL)")
    completed: int = Field(..., description="완료 여부 (0: 미완료, 1: 완료)")

    class Config:
        json_schema_extra = {
            "example": {
                "todo_id": 1,
                "todo": "바다 가서 사진 찍기",
                "credits": 100,
                "mission_type": "DAILY",
                "completed": 0
            }
        }


class MissionListResponse(BaseModel):
    """미션 목록 응답 DTO"""

    missions: List[MissionResponse] = Field(..., description="미션 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "missions": [
                    {
                        "todo_id": 1,
                        "todo": "바다 가서 사진 찍기",
                        "credits": 100,
                        "mission_type": "DAILY",
                        "completed": 0
                    },
                    {
                        "todo_id": 2,
                        "todo": "해양 생물 관찰하기",
                        "credits": 150,
                        "mission_type": "DAILY",
                        "completed": 1
                    }
                ]
            }
        }


class MissionCompleteResponse(BaseModel):
    """미션 완료 응답 DTO"""

    message: str = Field(..., description="완료 메시지")
    credits_earned: int = Field(..., description="획득한 크레딧")
    new_balance: int = Field(..., description="새로운 크레딧 잔액")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "미션을 완료했습니다.",
                "credits_earned": 100,
                "new_balance": 10100
            }
        }


class GarbageCollectionResponse(BaseModel):
    """쓰레기 수집 응답 DTO"""

    message: str = Field(..., description="수집 완료 메시지")
    credits_earned: int = Field(..., description="획득한 크레딧")
    new_balance: int = Field(..., description="새로운 크레딧 잔액")
    ocean_name: str = Field(..., description="해양 이름")
    garbage_collection_count: int = Field(..., description="해양 쓰레기 수집 총 횟수")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "쓰레기 수집을 완료했습니다.",
                "credits_earned": 100,
                "new_balance": 10200,
                "ocean_name": "해운대 해수욕장",
                "garbage_collection_count": 42
            }
        }
