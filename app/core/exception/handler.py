from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.exception.base import BaseCustomException


async def custom_exception_handler(request: Request, exc: BaseCustomException):
    """커스텀 예외 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"}
    )


def add_exception_handlers(app: FastAPI):
    """FastAPI 앱에 예외 핸들러 등록"""
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
