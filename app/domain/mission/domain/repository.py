from sqlalchemy.orm import Session
from typing import Optional, List
from app.domain.mission.domain.entity import Mission, UserMission, GarbageCollection
from app.domain.ocean.domain.entity import Ocean
from app.domain.auth.domain.entity import User
from datetime import datetime
import math


class MissionRepository:
    """미션 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def find_all_missions(self) -> List[Mission]:
        """
        모든 미션을 조회합니다.

        Returns:
            List[Mission]: 미션 목록
        """
        return self.db.query(Mission).all()

    def find_mission_by_id(self, todo_id: int) -> Optional[Mission]:
        """
        미션 ID로 미션을 조회합니다.

        Args:
            todo_id: 미션 ID

        Returns:
            Optional[Mission]: 조회된 미션 또는 None
        """
        return self.db.query(Mission).filter(Mission.todo_id == todo_id).first()

    def find_user_mission(self, user_id: str, todo_id: int) -> Optional[UserMission]:
        """
        사용자의 특정 미션 완료 기록을 조회합니다.

        Args:
            user_id: 사용자 ID
            todo_id: 미션 ID

        Returns:
            Optional[UserMission]: 조회된 사용자 미션 또는 None
        """
        return self.db.query(UserMission).filter(
            UserMission.user_id == user_id,
            UserMission.todo_id == todo_id
        ).first()

    def find_all_user_missions(self, user_id: str) -> List[UserMission]:
        """
        사용자의 모든 미션 완료 기록을 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            List[UserMission]: 사용자 미션 목록
        """
        return self.db.query(UserMission).filter(UserMission.user_id == user_id).all()

    def create_user_mission(self, user_id: str, todo_id: int) -> UserMission:
        """
        사용자 미션 완료 기록을 생성합니다.

        Args:
            user_id: 사용자 ID
            todo_id: 미션 ID

        Returns:
            UserMission: 생성된 사용자 미션
        """
        user_mission = UserMission(
            user_id=user_id,
            todo_id=todo_id,
            completed=0
        )
        self.db.add(user_mission)
        self.db.commit()
        self.db.refresh(user_mission)
        return user_mission

    def update_user_mission_completed(self, user_mission: UserMission) -> UserMission:
        """
        사용자 미션을 완료 상태로 업데이트합니다.

        Args:
            user_mission: 사용자 미션 객체

        Returns:
            UserMission: 업데이트된 사용자 미션
        """
        user_mission.completed = 1
        user_mission.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user_mission)
        return user_mission

    def find_user_by_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

    def update_user_credits(self, user: User, credits: int) -> User:
        """
        사용자의 크레딧을 업데이트합니다.

        Args:
            user: 사용자 객체
            credits: 추가할 크레딧

        Returns:
            User: 업데이트된 사용자
        """
        user.credits += credits
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_ocean_by_location(self, lat: float, lon: float, max_distance: float = 100.0) -> Optional[Ocean]:
        """
        위치에서 가장 가까운 해양을 조회합니다.

        Args:
            lat: 위도
            lon: 경도
            max_distance: 최대 거리 (km, 기본: 100km)

        Returns:
            Optional[Ocean]: 가장 가까운 해양 또는 None
        """
        # 모든 해양 조회
        all_oceans = self.db.query(Ocean).all()

        if not all_oceans:
            return None

        # 가장 가까운 해양 찾기
        closest_ocean = None
        min_distance = float('inf')

        for ocean in all_oceans:
            # 거리 계산 (유클리드 거리 -> km로 변환)
            # 위도/경도 1도는 약 111km
            distance = math.sqrt(
                ((ocean.lat - lat) * 111) ** 2 +
                ((ocean.lon - lon) * 111) ** 2
            )

            if distance < min_distance:
                min_distance = distance
                closest_ocean = ocean

        # 최대 거리 내에 있는 경우만 반환
        if closest_ocean and min_distance <= max_distance:
            return closest_ocean

        return None

    def create_garbage_collection(
        self,
        ocean_id: int,
        user_id: str,
        lat: float,
        lon: float,
        image_url: str,
        credits_earned: int
    ) -> GarbageCollection:
        """
        쓰레기 수집 기록을 생성합니다.

        Args:
            ocean_id: 해양 ID
            user_id: 사용자 ID
            lat: 수집 위치 위도
            lon: 수집 위치 경도
            image_url: 수집 사진 URL
            credits_earned: 획득 크레딧

        Returns:
            GarbageCollection: 생성된 쓰레기 수집 기록
        """
        garbage_collection = GarbageCollection(
            ocean_id=ocean_id,
            user_id=user_id,
            lat=lat,
            lon=lon,
            image_url=image_url,
            credits_earned=credits_earned
        )
        self.db.add(garbage_collection)
        self.db.commit()
        self.db.refresh(garbage_collection)
        return garbage_collection

    def increase_ocean_garbage_count(self, ocean: Ocean) -> Ocean:
        """
        해양의 쓰레기 수집 횟수를 증가시킵니다.

        Args:
            ocean: 해양 객체

        Returns:
            Ocean: 업데이트된 해양
        """
        ocean.garbage_collection_count += 1
        self.db.commit()
        self.db.refresh(ocean)
        return ocean

    def count_missions(self) -> int:
        """
        전체 미션 개수를 조회합니다.

        Returns:
            int: 미션 개수
        """
        return self.db.query(Mission).count()

    def create_mission(self, todo: str, credits: int, mission_type: str) -> Mission:
        """
        새로운 미션을 생성합니다.

        Args:
            todo: 미션 내용
            credits: 보상 크레딧
            mission_type: 미션 타입 (DAILY, SPECIAL)

        Returns:
            Mission: 생성된 미션
        """
        from app.domain.mission.domain.entity import MissionType

        # mission_type을 Enum으로 변환
        if mission_type == "SPECIAL":
            mt = MissionType.SPECIAL
        else:
            mt = MissionType.DAILY

        mission = Mission(
            todo=todo,
            credits=credits,
            mission_type=mt
        )
        self.db.add(mission)
        self.db.commit()
        self.db.refresh(mission)
        return mission
