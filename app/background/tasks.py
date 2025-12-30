"""
백그라운드 작업

주기적으로 실행되는 작업들을 정의합니다:
1. 기사 수집 및 시세 업데이트
2. 쓰레기 수집 횟수에 따른 시세 업데이트
3. 빌딩/음식점 수익금 자동 지급
4. 해양 관측소 데이터 수집 및 시세 업데이트
"""

import httpx
import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.domain.article.domain.entity import Article, ArticleSentiment
from app.domain.ocean.domain.entity import Ocean, WaterQuality
from app.domain.ocean_management.domain.entity import Building, BuildingType
from app.domain.auth.domain.entity import User
from app.config import get_settings

settings = get_settings()


async def fetch_and_update_articles():
    """
    주기적으로 뉴스 기사를 수집하고 시세를 업데이트합니다.

    1. 뉴스 API에서 해양 관련 기사 조회
    2. 기사 제목에 해양 이름이 포함된 기사만 필터링
    3. 기사 내용을 기반으로 감성 분석 (긍정/부정/중립)
    4. 기사에 따라 해양 시세 업데이트
    5. DB에 기사 저장 (이미지 포함)
    """
    db: Session = SessionLocal()

    try:
        # 모든 해양 조회
        oceans = db.query(Ocean).all()

        # 전체 해양 관련 뉴스를 한 번에 검색
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.NEWS_API_URL,
                    params={
                        "apiKey": settings.NEWS_API_KEY,
                        "q": "해양 OR 바다 OR 해수욕장 OR 항구",
                        "language": "ko",
                        "sortBy": "publishedAt",
                        "pageSize": 50  # 더 많은 기사 가져오기
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    print(f"뉴스 API 오류: HTTP {response.status_code}")
                    return

                data = response.json()
                articles_data = data.get("articles", [])

                for article_data in articles_data:
                    url = article_data.get("url")
                    title = article_data.get("title")
                    description = article_data.get("description", "")
                    content = article_data.get("content", "")
                    image_url = article_data.get("urlToImage")

                    if not url or not title:
                        continue

                    # 이미 저장된 기사인지 확인
                    existing = db.query(Article).filter(Article.url == url).first()
                    if existing:
                        continue

                    # 제목에 해양 이름이 포함되어 있는지 확인
                    matched_ocean = None
                    for ocean in oceans:
                        # 해양 이름의 주요 키워드 추출 (예: "해운대 앞바다" -> "해운대")
                        ocean_keywords = ocean.ocean_name.replace(" 앞바다", "").replace(" 해역", "")

                        if ocean_keywords in title:
                            matched_ocean = ocean
                            break

                    # 매칭되는 해양이 없으면 스킵
                    if not matched_ocean:
                        continue

                    # 기사 내용 준비 (description이나 content 사용)
                    article_content = description or content or ""
                    if len(article_content) > 2000:
                        article_content = article_content[:2000]

                    # 기사 내용 기반 감성 분석
                    sentiment = analyze_article_sentiment(title, article_content)

                    # 가격 변동량 계산
                    price_change = 0
                    if sentiment == ArticleSentiment.POSITIVE:
                        price_change = 150  # 긍정 기사: +150
                    elif sentiment == ArticleSentiment.NEGATIVE:
                        price_change = -150  # 부정 기사: -150

                    # 기사 저장
                    new_article = Article(
                        ocean_id=matched_ocean.ocean_id,
                        ocean_name=matched_ocean.ocean_name,
                        title=title,
                        content=article_content,
                        url=url,
                        image_url=image_url,
                        sentiment=sentiment,
                        price_change=price_change
                    )
                    db.add(new_article)

                    # 해양 시세 업데이트
                    matched_ocean.current_price += price_change
                    if matched_ocean.current_price < 100:  # 최소 가격 보장
                        matched_ocean.current_price = 100

                db.commit()

        except Exception as e:
            print(f"기사 수집 오류: {e}")
            db.rollback()

    except Exception as e:
        print(f"기사 수집 작업 오류: {e}")
        db.rollback()
    finally:
        db.close()


def analyze_article_sentiment(title: str, content: str) -> ArticleSentiment:
    """
    기사 제목과 내용을 기반으로 감성 분석 (키워드 기반)

    Args:
        title: 기사 제목
        content: 기사 내용

    Returns:
        ArticleSentiment: 긍정/부정/중립
    """
    positive_keywords = [
        "보존", "개선", "깨끗", "회복", "성공", "발전", "증가", "좋은",
        "활성화", "성장", "청정", "아름다운", "안전", "보호", "쾌적",
        "개발", "투자", "관광", "축제", "활기", "번창"
    ]
    negative_keywords = [
        "오염", "위험", "감소", "파괴", "악화", "문제", "피해",
        "쓰레기", "사고", "폐기물", "유출", "적조", "녹조", "침식",
        "폐쇄", "금지", "손실", "훼손", "취약", "우려"
    ]

    # 제목과 내용을 합쳐서 분석
    full_text = (title + " " + content).lower()

    positive_count = sum(1 for keyword in positive_keywords if keyword in full_text)
    negative_count = sum(1 for keyword in negative_keywords if keyword in full_text)

    # 더 강한 가중치로 판단
    if positive_count > negative_count:
        return ArticleSentiment.POSITIVE
    elif negative_count > positive_count:
        return ArticleSentiment.NEGATIVE
    else:
        return ArticleSentiment.NEUTRAL


async def update_ocean_prices_by_garbage():
    """
    쓰레기 수집 횟수에 따라 해양 시세를 업데이트합니다.

    - 쓰레기 수집이 많을수록 시세 상승
    - 쓰레기 수집이 적으면 시세 하락
    - 일정 기간 동안 쓰레기 수집이 부족하면 강제 경매
    """
    db: Session = SessionLocal()

    try:
        oceans = db.query(Ocean).all()

        for ocean in oceans:
            # 쓰레기 수집 횟수에 따른 가격 변동
            if ocean.garbage_collection_count > 100:
                price_change = 500  # 많이 수집: +500
            elif ocean.garbage_collection_count > 50:
                price_change = 300  # 보통 수집: +300
            elif ocean.garbage_collection_count > 20:
                price_change = 100  # 조금 수집: +100
            elif ocean.garbage_collection_count > 0:
                price_change = 0  # 최소 수집: 유지
            else:
                price_change = -200  # 수집 없음: -200

            ocean.current_price += price_change
            if ocean.current_price < 100:
                ocean.current_price = 100

            # TODO: 일정 기간 쓰레기 수집이 부족하면 강제 경매 로직 추가

        db.commit()

    except Exception as e:
        print(f"쓰레기 수집 기반 시세 업데이트 오류: {e}")
        db.rollback()
    finally:
        db.close()


async def generate_building_income():
    """
    빌딩/음식점에서 발생하는 수익금을 자동으로 지급합니다.

    1초마다 실행되며, 각 건물의 수익률에 따라 소유자에게 크레딧을 지급합니다.
    """
    db: Session = SessionLocal()

    try:
        # 모든 건물 조회
        buildings = db.query(Building).all()

        for building in buildings:
            # 마지막 수익금 지급 이후 경과 시간 계산 (초 단위)
            now = datetime.utcnow()
            elapsed_seconds = (now - building.last_income_generated_at).total_seconds()

            if elapsed_seconds >= 1:  # 1초 이상 경과
                # 수익금 계산
                income = int(elapsed_seconds) * building.income_rate

                # 소유자에게 크레딧 지급
                owner = db.query(User).filter(User.user_id == building.user_id).first()
                if owner:
                    owner.credits += income

                # 마지막 수익금 지급 시간 업데이트
                building.last_income_generated_at = now

        db.commit()

    except Exception as e:
        print(f"수익금 지급 오류: {e}")
        db.rollback()
    finally:
        db.close()


async def fetch_and_update_ocean_data():
    """
    해양 관측소 데이터를 수집하고 시세를 업데이트합니다.

    1. Ocean Data API에서 관측소 정보 조회
    2. 각 해양 지역과 가장 가까운 관측소 찾기
    3. 관측소 유형에 따라 시세 업데이트
       - 종합해양과학기지: +200 (가장 체계적 관리)
       - 해양관측부이: +150 (일반 관리)
       - 조위관측소: +100 (기본 관리)
    """
    db: Session = SessionLocal()

    try:
        # Ocean Data API에서 관측소 정보 가져오기
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.OCEAN_DATA_API_URL,
                params={
                    "page": 1,
                    "perPage": 100,  # 전체 100개 관측소 조회
                    "serviceKey": settings.OCEAN_DATA_API_KEY
                },
                timeout=10.0
            )

            if response.status_code != 200:
                print(f"Ocean Data API 오류: HTTP {response.status_code}")
                return

            data = response.json()
            stations = data.get("data", [])

            if not stations:
                print("관측소 데이터가 없습니다.")
                return

            # 모든 해양 조회
            oceans = db.query(Ocean).all()

            for ocean in oceans:
                # 해양과 가장 가까운 관측소 찾기
                closest_station = None
                min_distance = float('inf')

                for station in stations:
                    try:
                        station_lat = float(station.get("위도", 0))
                        station_lon = float(station.get("경도", 0))

                        # 거리 계산 (간단한 유클리드 거리)
                        distance = math.sqrt(
                            (ocean.lat - station_lat) ** 2 +
                            (ocean.lon - station_lon) ** 2
                        )

                        if distance < min_distance:
                            min_distance = distance
                            closest_station = station
                    except (ValueError, TypeError):
                        continue

                if closest_station and min_distance < 1.0:  # 약 111km 이내
                    # 관측소 유형에 따라 가격 변동
                    station_type = closest_station.get("관측소 유형", "")

                    if "종합해양과학기지" in station_type:
                        price_change = 200
                    elif "해양관측부이" in station_type:
                        price_change = 150
                    elif "조위관측소" in station_type:
                        price_change = 100
                    else:
                        price_change = 50

                    # 시세 업데이트
                    ocean.current_price += price_change
                    if ocean.current_price < 100:
                        ocean.current_price = 100

                    # 수질 데이터 업데이트 (관측소 정보 기반)
                    water_quality = db.query(WaterQuality).filter(
                        WaterQuality.ocean_id == ocean.ocean_id
                    ).first()

                    if not water_quality:
                        # 새로운 수질 데이터 생성
                        water_quality = WaterQuality(
                            ocean_id=ocean.ocean_id,
                            temperature=20.0,  # 기본값
                            ph=8.0,  # 기본값
                            dissolved_oxygen=7.0,  # 기본값
                            salinity=35.0,  # 기본값
                            pollution_level="GOOD",
                            observation_station=closest_station.get("관측소 명"),
                            station_code=closest_station.get("관측소 코드명")
                        )
                        db.add(water_quality)
                    else:
                        # 기존 수질 데이터 업데이트
                        water_quality.observation_station = closest_station.get("관측소 명")
                        water_quality.station_code = closest_station.get("관측소 코드명")
                        water_quality.measured_at = datetime.utcnow()

            db.commit()
            print(f"해양 관측소 데이터 업데이트 완료: {len(stations)}개 관측소")

    except Exception as e:
        print(f"해양 관측소 데이터 수집 오류: {e}")
        db.rollback()
    finally:
        db.close()
