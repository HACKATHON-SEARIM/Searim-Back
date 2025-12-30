from openai import AsyncOpenAI
from PIL import Image
import io
import json
import base64
from typing import Optional, Dict
from app.config import get_settings

settings = get_settings()


class OpenAIClient:
    """
    OpenAI API 클라이언트

    이미지 분석 및 인증에 사용됩니다.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _encode_image(self, image_bytes: bytes) -> str:
        """이미지를 base64로 인코딩합니다."""
        return base64.b64encode(image_bytes).decode('utf-8')

    async def verify_garbage_image(self, image_bytes: bytes) -> bool:
        """
        쓰레기 이미지 검증

        Args:
            image_bytes: 이미지 바이트 데이터

        Returns:
            bool: 쓰레기 사진이면 True, 아니면 False
        """
        try:
            # 이미지를 base64로 인코딩
            base64_image = self._encode_image(image_bytes)

            # OpenAI에게 쓰레기 여부 확인 요청
            prompt = """
            이 이미지에 쓰레기가 포함되어 있나요?
            쓰레기는 플라스틱 병, 비닐봉지, 캔, 종이, 담배꽁초 등 해양 오염을 유발하는 모든 버려진 물건을 의미합니다.

            다음 중 하나로만 답변해주세요:
            - "YES": 쓰레기가 명확하게 보이는 경우
            - "NO": 쓰레기가 보이지 않거나 불명확한 경우
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100
            )

            result = response.choices[0].message.content.strip().upper()
            return "YES" in result

        except Exception as e:
            print(f"OpenAI API 오류: {e}")
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
            # 이미지를 base64로 인코딩
            base64_image = self._encode_image(image_bytes)

            # OpenAI에게 바다 배경 여부 확인 요청
            prompt = """
            이 이미지의 배경이 바다(해양)인가요?
            바다는 바닷물, 파도, 해변, 항구, 선박 등 해양과 관련된 모든 것을 포함합니다.

            다음 중 하나로만 답변해주세요:
            - "YES": 바다 배경이 명확하게 보이는 경우
            - "NO": 바다 배경이 아니거나 불명확한 경우
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100
            )

            result = response.choices[0].message.content.strip().upper()
            return "YES" in result

        except Exception as e:
            print(f"OpenAI API 오류: {e}")
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
            # 이미지를 base64로 인코딩
            base64_image = self._encode_image(image_bytes)

            # OpenAI에게 미션 완료 여부 확인 요청
            prompt = f"""
            사용자가 다음 미션을 완료하려고 합니다: "{mission_description}"

            이 이미지가 해당 미션을 완료했음을 증명하나요?

            다음 중 하나로만 답변해주세요:
            - "YES": 이미지가 미션 완료를 명확하게 증명하는 경우
            - "NO": 이미지가 미션과 무관하거나 불명확한 경우
            너무 빡빡하게 검증하기 보다는 정당히 비슷하다면 YES를 리턴하고 비슷하지 않다면 NO를 리턴해주세요
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100
            )

            result = response.choices[0].message.content.strip().upper()
            return "YES" in result

        except Exception as e:
            print(f"OpenAI API 오류: {e}")
            return False

    async def analyze_article_sentiment(self, ocean_name: str, article_title: str, article_content: str) -> str:
        """
        기사 내용을 분석하여 해당 해양에 대한 감성을 판단합니다.

        Args:
            ocean_name: 해양 이름 (예: "해운대 앞바다")
            article_title: 기사 제목
            article_content: 기사 내용

        Returns:
            str: "positive" (긍정), "negative" (부정), "neutral" (중립)
        """
        try:
            # OpenAI에게 감성 분석 요청
            prompt = f"""
            다음 기사가 "{ocean_name}" 해양 지역에 대해 긍정적인지, 부정적인지, 중립적인지 판단해주세요.

            기사 제목: {article_title}
            기사 내용: {article_content[:500]}

            판단 기준:
            - 긍정적: 수질 개선, 환경 보호, 관광 활성화, 생태계 회복, 투자, 개발 등
            - 부정적: 오염, 쓰레기, 환경 파괴, 적조, 사고, 피해 등
            - 중립적: 단순 정보 전달, 통계, 일반 소식 등

            다음 중 하나로만 답변해주세요:
            - "positive": 해양에 긍정적인 영향
            - "negative": 해양에 부정적인 영향
            - "neutral": 중립적이거나 판단 불가

            답변은 반드시 하나의 단어만 출력하세요 (positive, negative, neutral 중 하나).
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )

            result = response.choices[0].message.content.strip().lower()

            # 결과 검증
            if "positive" in result:
                return "positive"
            elif "negative" in result:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            print(f"OpenAI 감성 분석 오류: {e}")
            return "neutral"  # 오류 시 중립으로 처리

    async def generate_mission(self) -> Optional[Dict]:
        """
        AI를 사용하여 새로운 해양 관련 미션을 생성합니다.

        Returns:
            Optional[Dict]: 생성된 미션 정보 {"todo": str, "credits": int, "mission_type": str}
                           실패 시 None
        """
        try:
            # OpenAI에게 미션 생성 요청
            prompt = """
            해양 환경 보호와 관련된 창의적인 미션을 1개 생성해주세요.

            미션 종류:
            - DAILY: 일일 미션 (예: "해변에서 일몰 사진 찍기", "바다 근처에서 산책하기")
            - SPECIAL: 특별 미션 (예: "해양 쓰레기 10개 수거하기", "해양 박물관 방문하기")

            미션은 다양하고 창의적이어야 하며, 실제로 실행 가능해야 합니다.

            응답은 반드시 다음 JSON 형식으로만 작성하세요:
            {
                "todo": "미션 설명 (한국어, 50자 이내)",
                "credits": 보상 크레딧 (100-500 사이 정수),
                "mission_type": "DAILY 또는 SPECIAL"
            }

            JSON만 출력하고 다른 텍스트는 포함하지 마세요.
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content.strip()

            # JSON 파싱
            mission_data = json.loads(result_text)

            # 필수 필드 검증
            if not all(k in mission_data for k in ["todo", "credits", "mission_type"]):
                print(f"AI 미션 생성 오류: 필수 필드 누락 - {mission_data}")
                return None

            # 미션 타입 검증
            if mission_data["mission_type"] not in ["DAILY", "SPECIAL"]:
                mission_data["mission_type"] = "DAILY"

            # 크레딧 범위 검증
            if not (100 <= mission_data["credits"] <= 500):
                mission_data["credits"] = min(max(mission_data["credits"], 100), 500)

            return mission_data

        except json.JSONDecodeError as e:
            print(f"OpenAI AI JSON 파싱 오류: {e}\n응답: {result_text}")
            return None
        except Exception as e:
            print(f"OpenAI AI 미션 생성 오류: {e}")
            return None


# 싱글톤 인스턴스
openai_client = OpenAIClient()
