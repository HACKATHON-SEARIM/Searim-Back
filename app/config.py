from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Model Selection
    AI_MODEL_PROVIDER: str = "openai"  # "openai" or "gemini"

    # Gemini API
    GEMINI_API_KEY: str = ""

    # OpenAI API
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # gpt-4, gpt-4o-mini, gpt-3.5-turbo 등

    # News API
    NEWS_API_KEY: str
    NEWS_API_URL: str

    # Ocean Data API
    OCEAN_DATA_API_KEY: str
    OCEAN_DATA_API_URL: str

    # Application
    APP_TITLE: str = "Marine Real Estate API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "해양 부동산 관리 및 거래 플랫폼 API"

    # Background Tasks
    ARTICLE_FETCH_INTERVAL_MINUTES: int = 60  # 1시간마다 기사 수집
    INCOME_GENERATION_INTERVAL_SECONDS: int = 10  # 10초마다 수익금 지급
    PRICE_UPDATE_INTERVAL_MINUTES: int = 10  # 10분마다 시세 업데이트
    OCEAN_DATA_FETCH_INTERVAL_MINUTES: int = 30  # 30분마다 해양 관측소 데이터 수집

    # Building Costs (건물 구매 비용)
    STORE_COST: int = 100000  # 가게 구매 비용 (10만 크레딧)
    BUILDING_COST: int = 500000  # 빌딩 구매 비용 (50만 크레딧)

    # Building Income Rates (크레딧/초)
    # 가게: 10초에 10만의 4% = 4,000 크레딧 → 초당 400 크레딧
    # 빌딩: 10초에 50만의 4% = 20,000 크레딧 → 초당 2,000 크레딧
    STORE_INCOME_RATE: int = 400  # 음식점 수익률 (크레딧/초)
    BUILDING_INCOME_RATE: int = 2000  # 빌딩 수익률 (크레딧/초)

    # Garbage Collection Reward
    GARBAGE_BASE_REWARD: int = 100  # 기본 쓰레기 수집 보상

    # Initial Credits
    INITIAL_CREDITS: int = 99999999  # 신규 가입시 지급 크레딧 (시연용)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()
