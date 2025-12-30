from sqlalchemy.orm import Session
from typing import List, Dict
from fastapi import HTTPException, status, UploadFile
from app.domain.mission.domain.repository import MissionRepository
from app.core.ai.gemini_client import gemini_client
from app.config import get_settings
import uuid
import os

settings = get_settings()


class MissionService:
    """미션 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = MissionRepository(db)

    def get_missions(self, user_id: str) -> List[Dict]:
        """
        미션 목록을 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            List[Dict]: 미션 목록 (완료 여부 포함)
        """
        # 모든 미션 조회
        missions = self.repository.find_all_missions()

        # 사용자의 미션 완료 기록 조회
        user_missions = self.repository.find_all_user_missions(user_id)
        user_mission_map = {um.todo_id: um.completed for um in user_missions}

        # 미션 목록 생성
        mission_list = []
        for mission in missions:
            mission_list.append({
                "todo_id": mission.todo_id,
                "todo": mission.todo,
                "credits": mission.credits,
                "mission_type": mission.mission_type.value,
                "completed": user_mission_map.get(mission.todo_id, 0)
            })

        return mission_list

    async def complete_mission(self, user_id: str, todo_id: int, image: UploadFile) -> Dict:
        """
        미션을 완료합니다.

        Args:
            user_id: 사용자 ID
            todo_id: 미션 ID
            image: 미션 완료 사진

        Returns:
            Dict: 완료 결과 (credits_earned, new_balance)

        Raises:
            HTTPException: 미션이 존재하지 않거나 이미 완료된 경우
        """
        # 미션 조회
        mission = self.repository.find_mission_by_id(todo_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="미션을 찾을 수 없습니다."
            )

        # 사용자 미션 완료 기록 조회 또는 생성
        user_mission = self.repository.find_user_mission(user_id, todo_id)
        if not user_mission:
            user_mission = self.repository.create_user_mission(user_id, todo_id)

        # 이미 완료한 미션인지 확인
        if user_mission.completed == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 완료한 미션입니다."
            )

        # 이미지 검증 (Gemini API 사용)
        image_bytes = await image.read()
        is_valid = await gemini_client.verify_mission_image(image_bytes, mission.todo)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="미션 완료 조건을 만족하지 않습니다. 올바른 사진을 업로드해주세요."
            )

        # 미션 완료 처리
        self.repository.update_user_mission_completed(user_mission)

        # 사용자 크레딧 지급
        user = self.repository.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        self.repository.update_user_credits(user, mission.credits)

        return {
            "message": "미션을 완료했습니다.",
            "credits_earned": mission.credits,
            "new_balance": user.credits
        }

    async def collect_garbage(
        self,
        user_id: str,
        lat: float,
        lon: float,
        image: UploadFile
    ) -> Dict:
        """
        쓰레기를 수집합니다.

        Args:
            user_id: 사용자 ID
            lat: 수집 위치 위도
            lon: 수집 위치 경도
            image: 쓰레기 사진

        Returns:
            Dict: 수집 결과 (credits_earned, new_balance, ocean_name, garbage_count)

        Raises:
            HTTPException: 해양을 찾을 수 없거나 쓰레기 사진이 아닌 경우
        """
        # 위치 기반 해양 조회
        ocean = self.repository.find_ocean_by_location(lat, lon)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 위치의 해양을 찾을 수 없습니다. 해양 근처에서 시도해주세요."
            )

        # 이미지 검증 (Gemini API 사용)
        image_bytes = await image.read()
        is_garbage = await gemini_client.verify_garbage_image(image_bytes)

        if not is_garbage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="쓰레기가 감지되지 않았습니다. 쓰레기 사진을 업로드해주세요."
            )

        # 이미지 저장 (임시로 로컬 경로 사용, 실제로는 S3 등에 저장)
        image_url = await self._save_image(image_bytes, image.filename)

        # 크레딧 계산
        credits_earned = settings.GARBAGE_BASE_REWARD

        # 쓰레기 수집 기록 생성
        self.repository.create_garbage_collection(
            ocean_id=ocean.ocean_id,
            user_id=user_id,
            lat=lat,
            lon=lon,
            image_url=image_url,
            credits_earned=credits_earned
        )

        # 해양 쓰레기 수집 횟수 증가
        self.repository.increase_ocean_garbage_count(ocean)

        # 사용자 크레딧 지급
        user = self.repository.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        self.repository.update_user_credits(user, credits_earned)

        return {
            "message": "쓰레기 수집을 완료했습니다.",
            "credits_earned": credits_earned,
            "new_balance": user.credits,
            "ocean_name": ocean.ocean_name,
            "garbage_collection_count": ocean.garbage_collection_count
        }

    async def _save_image(self, image_bytes: bytes, filename: str) -> str:
        """
        이미지를 저장합니다.

        Args:
            image_bytes: 이미지 바이트 데이터
            filename: 파일명

        Returns:
            str: 저장된 이미지 URL
        """
        # 임시 디렉토리 생성
        upload_dir = "/tmp/mission_images"
        os.makedirs(upload_dir, exist_ok=True)

        # 고유 파일명 생성
        file_extension = filename.split(".")[-1] if "." in filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        # 실제로는 S3 등에 업로드하고 URL 반환
        # 임시로 로컬 경로 반환
        return file_path
