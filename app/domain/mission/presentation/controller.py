from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.domain.mission.application.service import MissionService
from app.domain.mission.presentation.dto import (
    MissionResponse,
    MissionListResponse,
    MissionCompleteResponse,
    GarbageCollectionResponse
)
from app.core.security.jwt import get_current_username

router = APIRouter(prefix="/mission", tags=["Mission"])


@router.get(
    "",
    response_model=MissionListResponse,
    status_code=status.HTTP_200_OK,
    summary="미션 목록 조회",
    description="전체 미션 목록과 사용자의 완료 여부를 조회합니다. 인증이 필요합니다."
)
async def get_missions(
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db)
) -> MissionListResponse:
    """
    미션 목록 조회 엔드포인트

    Args:
        username: 현재 로그인한 사용자 이름 (JWT에서 추출)
        db: 데이터베이스 세션

    Returns:
        MissionListResponse: 미션 목록 (완료 여부 포함)

    Raises:
        HTTPException 401: 인증 실패
    """
    service = MissionService(db)
    missions = service.get_missions(username)

    # DTO로 변환
    mission_responses = [
        MissionResponse(
            todo_id=mission["todo_id"],
            todo=mission["todo"],
            credits=mission["credits"],
            mission_type=mission["mission_type"],
            completed=mission["completed"]
        )
        for mission in missions
    ]

    return MissionListResponse(missions=mission_responses)


@router.post(
    "/{todo_id}",
    response_model=MissionCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="미션 완료",
    description="미션 완료 사진을 업로드하여 미션을 완료합니다. Gemini API로 사진을 검증하고, 성공 시 크레딧을 지급합니다. 인증이 필요합니다."
)
async def complete_mission(
    todo_id: int,
    image: UploadFile = File(..., description="미션 완료 사진"),
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db)
) -> MissionCompleteResponse:
    """
    미션 완료 엔드포인트

    Args:
        todo_id: 미션 ID
        image: 미션 완료 사진 (multipart/form-data)
        username: 현재 로그인한 사용자 이름 (JWT에서 추출)
        db: 데이터베이스 세션

    Returns:
        MissionCompleteResponse: 완료 결과 (획득 크레딧, 새로운 잔액)

    Raises:
        HTTPException 400: 이미 완료한 미션이거나 사진 검증 실패
        HTTPException 401: 인증 실패
        HTTPException 404: 미션을 찾을 수 없음
    """
    service = MissionService(db)
    result = await service.complete_mission(username, todo_id, image)

    return MissionCompleteResponse(
        message=result["message"],
        credits_earned=result["credits_earned"],
        new_balance=result["new_balance"]
    )


@router.post(
    "/ocean/garbage/collection",
    response_model=GarbageCollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="쓰레기 수집",
    description="해양 쓰레기 수집 사진을 업로드합니다. Gemini API로 쓰레기 사진을 검증하고, 성공 시 크레딧을 지급하며 해양 쓰레기 수집 횟수를 증가시킵니다. 인증이 필요합니다."
)
async def collect_garbage(
    lat: float = Query(..., description="수집 위치 위도"),
    lon: float = Query(..., description="수집 위치 경도"),
    image: UploadFile = File(..., description="쓰레기 수집 사진"),
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db)
) -> GarbageCollectionResponse:
    """
    쓰레기 수집 엔드포인트

    Args:
        lat: 수집 위치 위도
        lon: 수집 위치 경도
        image: 쓰레기 수집 사진 (multipart/form-data)
        username: 현재 로그인한 사용자 이름 (JWT에서 추출)
        db: 데이터베이스 세션

    Returns:
        GarbageCollectionResponse: 수집 결과 (획득 크레딧, 새로운 잔액, 해양 이름, 수집 횟수)

    Raises:
        HTTPException 400: 쓰레기 사진이 아닌 경우
        HTTPException 401: 인증 실패
        HTTPException 404: 해양을 찾을 수 없음
    """
    service = MissionService(db)
    result = await service.collect_garbage(username, lat, lon, image)

    return GarbageCollectionResponse(
        message=result["message"],
        credits_earned=result["credits_earned"],
        new_balance=result["new_balance"],
        ocean_name=result["ocean_name"],
        garbage_collection_count=result["garbage_collection_count"]
    )
