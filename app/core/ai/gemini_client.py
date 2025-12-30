import google.generativeai as genai
from PIL import Image
import io
from typing import Optional
from app.config import get_settings

settings = get_settings()

# Gemini API 설정
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiClient:
    """
    Google Gemini API 클라이언트

    이미지 분석 및 인증에 사용됩니다.
    """

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def verify_garbage_image(self, image_bytes: bytes) -> bool:
        """
        쓰레기 이미지 검증

        Args:
            image_bytes: 이미지 바이트 데이터

        Returns:
            bool: 쓰레기 사진이면 True, 아니면 False
        """
        try:
            # 이미지 로드
            image = Image.open(io.BytesIO(image_bytes))

            # Gemini에게 쓰레기 여부 확인 요청
            prompt = """
            이 이미지에 쓰레기가 포함되어 있나요?
            쓰레기는 플라스틱 병, 비닐봉지, 캔, 종이, 담배꽁초 등 해양 오염을 유발하는 모든 버려진 물건을 의미합니다.

            다음 중 하나로만 답변해주세요:
            - "YES": 쓰레기가 명확하게 보이는 경우
            - "NO": 쓰레기가 보이지 않거나 불명확한 경우
            """

            response = self.model.generate_content([prompt, image])
            result = response.text.strip().upper()

            return "YES" in result

        except Exception as e:
            print(f"Gemini API 오류: {e}")
            return False

    async def verify_ocean_background(self, image_bytes: bytes) -> bool:
        """
        바다 배경 이미지 검증

        Args:
            image_bytes: 이미지 바이트 데이터

        Returns:
            bool: 바다 배경이면 True, 아니면 False
        """
        try:
            # 이미지 로드
            image = Image.open(io.BytesIO(image_bytes))

            # Gemini에게 바다 배경 여부 확인 요청
            prompt = """
            이 이미지의 배경이 바다(해양)인가요?
            바다는 바닷물, 파도, 해변, 항구, 선박 등 해양과 관련된 모든 것을 포함합니다.

            다음 중 하나로만 답변해주세요:
            - "YES": 바다 배경이 명확하게 보이는 경우
            - "NO": 바다 배경이 아니거나 불명확한 경우
            """

            response = self.model.generate_content([prompt, image])
            result = response.text.strip().upper()

            return "YES" in result

        except Exception as e:
            print(f"Gemini API 오류: {e}")
            return False

    async def verify_mission_image(self, image_bytes: bytes, mission_description: str) -> bool:
        """
        미션 완료 이미지 검증

        Args:
            image_bytes: 이미지 바이트 데이터
            mission_description: 미션 설명 (예: "바다 가서 사진 찍기")

        Returns:
            bool: 미션 조건을 만족하면 True, 아니면 False
        """
        try:
            # 이미지 로드
            image = Image.open(io.BytesIO(image_bytes))

            # Gemini에게 미션 완료 여부 확인 요청
            prompt = f"""
            사용자가 다음 미션을 완료하려고 합니다: "{mission_description}"

            이 이미지가 해당 미션을 완료했음을 증명하나요?

            다음 중 하나로만 답변해주세요:
            - "YES": 이미지가 미션 완료를 명확하게 증명하는 경우
            - "NO": 이미지가 미션과 무관하거나 불명확한 경우
            """

            response = self.model.generate_content([prompt, image])
            result = response.text.strip().upper()

            return "YES" in result

        except Exception as e:
            print(f"Gemini API 오류: {e}")
            return False


# 싱글톤 인스턴스
gemini_client = GeminiClient()
