from fastapi import APIRouter, Depends, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.domain.auth.application.service import AuthService
from app.domain.auth.presentation.dto import SignupRequest, AuthResponse, UserInfoResponse, RankingItemResponse
from app.core.security.jwt import get_current_username

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 생성하고 JWT 액세스 토큰을 반환합니다. 초기 크레딧 10000이 자동으로 지급됩니다."
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    회원가입 엔드포인트

    Args:
        request: 회원가입 요청 (username, password)
        db: 데이터베이스 세션

    Returns:
        AuthResponse: JWT 액세스 토큰

    Raises:
        HTTPException 400: 이미 존재하는 사용자 이름인 경우
    """
    service = AuthService(db)
    access_token = service.signup(
        username=request.username,
        password=request.password
    )
    return AuthResponse(access_token=access_token)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="사용자 인증을 수행하고 JWT 액세스 토큰을 반환합니다. OAuth2 표준 형식을 사용합니다."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    로그인 엔드포인트

    Args:
        form_data: OAuth2 표준 로그인 폼 (username, password)
        db: 데이터베이스 세션

    Returns:
        AuthResponse: JWT 액세스 토큰

    Raises:
        HTTPException 401: 사용자 이름 또는 비밀번호가 올바르지 않은 경우
    """
    service = AuthService(db)
    access_token = service.login(
        username=form_data.username,
        password=form_data.password
    )
    return AuthResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다. JWT 인증이 필요합니다."
)
def get_my_info(
    current_username: str = Depends(get_current_username),
    db: Session = Depends(get_db)
) -> UserInfoResponse:
    """
    내 정보 조회 엔드포인트

    Args:
        current_username: 현재 로그인한 사용자 이름 (JWT에서 추출)
        db: 데이터베이스 세션

    Returns:
        UserInfoResponse: 사용자 정보

    Raises:
        HTTPException 404: 사용자를 찾을 수 없는 경우
    """
    service = AuthService(db)
    user_info = service.get_user_info(current_username)
    return UserInfoResponse(**user_info)


@router.get(
    "/ranking",
    response_model=List[RankingItemResponse],
    status_code=status.HTTP_200_OK,
    summary="크레딧 랭킹 조회",
    description="크레딧이 높은 순서로 사용자 랭킹을 조회합니다."
)
def get_ranking(
    limit: int = Query(10, description="조회할 사용자 수", ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[RankingItemResponse]:
    """
    크레딧 랭킹 조회 엔드포인트

    Args:
        limit: 조회할 사용자 수 (기본값: 10, 최대: 100)
        db: 데이터베이스 세션

    Returns:
        List[RankingItemResponse]: 랭킹 목록

    Example Response:
        [
            {
                "rank": 1,
                "username": "huhon",
                "credits": 50000
            },
            {
                "rank": 2,
                "username": "user2",
                "credits": 30000
            }
        ]
    """
    service = AuthService(db)
    ranking = service.get_ranking(limit)
    return [RankingItemResponse(**item) for item in ranking]
