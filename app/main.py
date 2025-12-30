from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.database import init_db
from app.core.exception.handler import add_exception_handlers
from app.background.tasks import (
    fetch_and_update_articles,
    update_ocean_prices_by_garbage,
    generate_building_income,
    fetch_and_update_ocean_data,
    finalize_expired_auctions
)

# 도메인별 라우터 import
from app.domain.auth.presentation.controller import router as auth_router
from app.domain.ocean.presentation.controller import router as ocean_router
from app.domain.ocean_management.presentation.controller import router as ocean_management_router
from app.domain.ocean_trade.presentation.controller import router as ocean_trade_router
from app.domain.mission.presentation.controller import router as mission_router
from app.domain.article.presentation.controller import router as article_router

settings = get_settings()
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 라이프사이클 관리

    시작 시: 데이터베이스 초기화 및 백그라운드 작업 시작
    종료 시: 스케줄러 종료
    """
    # 시작 시 실행
    init_db()

    # 서버 시작 시 백그라운드 작업 즉시 한 번 실행
    print("🚀 서버 시작 시 백그라운드 작업 초기 실행 중...")

    try:
        await fetch_and_update_articles()
        print("✅ 기사 수집 완료")
    except Exception as e:
        print(f"⚠️  기사 수집 오류: {e}")

    try:
        await update_ocean_prices_by_garbage()
        print("✅ 쓰레기 수집 기반 시세 업데이트 완료")
    except Exception as e:
        print(f"⚠️  쓰레기 수집 기반 시세 업데이트 오류: {e}")

    try:
        await fetch_and_update_ocean_data()
        print("✅ 해양 관측소 데이터 수집 완료")
    except Exception as e:
        print(f"⚠️  해양 관측소 데이터 수집 오류: {e}")

    # 미션 자동 생성 (5개 유지)
    try:
        from app.database import SessionLocal
        from app.domain.mission.application.service import MissionService

        db = SessionLocal()
        try:
            mission_service = MissionService(db)
            await mission_service.check_and_generate_missions()
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  미션 자동 생성 오류: {e}")

    # generate_building_income은 매 초마다 실행되므로 초기 실행 생략
    print("✅ 초기 백그라운드 작업 완료\n")

    # 백그라운드 작업 스케줄링
    # 1. 주기적으로 기사 수집 및 시세 업데이트 (1시간마다)
    scheduler.add_job(
        fetch_and_update_articles,
        'interval',
        minutes=settings.ARTICLE_FETCH_INTERVAL_MINUTES,
        id='fetch_articles'
    )

    # 2. 쓰레기 수집 횟수에 따른 시세 업데이트 (10분마다)
    scheduler.add_job(
        update_ocean_prices_by_garbage,
        'interval',
        minutes=settings.PRICE_UPDATE_INTERVAL_MINUTES,
        id='update_prices_by_garbage'
    )

    # 3. 빌딩/음식점 수익금 지급 (1초마다)
    scheduler.add_job(
        generate_building_income,
        'interval',
        seconds=settings.INCOME_GENERATION_INTERVAL_SECONDS,
        id='generate_building_income'
    )

    # 4. 해양 관측소 데이터 수집 및 시세 업데이트 (30분마다)
    scheduler.add_job(
        fetch_and_update_ocean_data,
        'interval',
        minutes=settings.OCEAN_DATA_FETCH_INTERVAL_MINUTES,
        id='fetch_ocean_data'
    )

    # 5. 경매 자동 종료 (1분마다)
    scheduler.add_job(
        finalize_expired_auctions,
        'interval',
        minutes=1,
        id='finalize_expired_auctions'
    )

    scheduler.start()
    print("📅 백그라운드 작업 스케줄러 시작됨\n")

    yield

    # 종료 시 실행
    scheduler.shutdown()


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러 등록
add_exception_handlers(app)

# 라우터 등록
app.include_router(auth_router, prefix="/api", tags=["인증/인가"])
app.include_router(ocean_router, prefix="/api", tags=["해양"])
app.include_router(ocean_management_router, prefix="/api", tags=["해양 관리"])
app.include_router(ocean_trade_router, prefix="/api", tags=["해양 거래"])
app.include_router(mission_router, prefix="/api", tags=["미션"])
app.include_router(article_router, prefix="/api", tags=["기사"])


@app.get("/")
async def root():
    """루트 엔드포인트 - API 상태 확인"""
    return {
        "message": "Marine Real Estate API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}
