"""
AI 클라이언트 팩토리

환경변수에 따라 적절한 AI 클라이언트를 반환합니다.
"""
from app.config import get_settings

settings = get_settings()


def get_ai_client():
    """
    환경변수에 따라 적절한 AI 클라이언트를 반환합니다.

    Returns:
        GeminiClient 또는 OpenAIClient 인스턴스
    """
    provider = settings.AI_MODEL_PROVIDER.lower()

    if provider == "openai":
        from app.core.ai.openai_client import openai_client
        return openai_client
    elif provider == "gemini":
        from app.core.ai.gemini_client import gemini_client
        return gemini_client
    else:
        # 기본값은 OpenAI
        print(f"⚠️ 알 수 없는 AI 모델 프로바이더: {provider}. OpenAI를 사용합니다.")
        from app.core.ai.openai_client import openai_client
        return openai_client


# 싱글톤 인스턴스 (편의를 위해)
ai_client = get_ai_client()
