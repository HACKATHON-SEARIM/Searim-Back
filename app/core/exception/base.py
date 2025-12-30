from fastapi import status


class BaseCustomException(Exception):
    """기본 커스텀 예외 클래스"""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BaseCustomException):
    """리소스를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(BaseCustomException):
    """인증되지 않은 사용자일 때 발생하는 예외"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BaseCustomException):
    """권한이 없을 때 발생하는 예외"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestException(BaseCustomException):
    """잘못된 요청일 때 발생하는 예외"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConflictException(BaseCustomException):
    """리소스 충돌이 발생했을 때의 예외"""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class InsufficientCreditsException(BaseCustomException):
    """크레딧이 부족할 때 발생하는 예외"""

    def __init__(self, message: str = "Insufficient credits"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
