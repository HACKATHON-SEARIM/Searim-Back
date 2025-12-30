from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.auth.application.service import AuthService
from app.domain.auth.presentation.dto import SignupRequest, AuthResponse

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
