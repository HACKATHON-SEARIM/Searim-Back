from sqlalchemy.orm import Session
from typing import Optional, List
from app.domain.mission.domain.entity import Mission, UserMission, GarbageCollection
from app.domain.ocean.domain.entity import Ocean
from app.domain.auth.domain.entity import User
from datetime import datetime


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

    def find_ocean_by_location(self, lat: float, lon: float, radius: float = 0.1) -> Optional[Ocean]:
        """
        위치 기반으로 해양을 조회합니다.

        Args:
            lat: 위도
            lon: 경도
            radius: 검색 반경 (기본: 0.1도, 약 11km)

        Returns:
            Optional[Ocean]: 조회된 해양 또는 None
        """
        return self.db.query(Ocean).filter(
            Ocean.lat.between(lat - radius, lat + radius),
            Ocean.lon.between(lon - radius, lon + radius)
        ).first()

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
