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
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.domain.article.domain.entity import Article, ArticleSentiment
from app.domain.ocean.domain.entity import Ocean, WaterQuality, WaterQualityStatus
from app.domain.ocean.domain.repository import OceanRepository
from app.domain.ocean_management.domain.entity import Building, BuildingType
from app.domain.auth.domain.entity import User
from app.config import get_settings
from app.core.ai.ai_client import ai_client

settings = get_settings()


def _record_ocean_price_history(repo: OceanRepository, ocean: Ocean, previous_price: int) -> None:
    if ocean.current_price != previous_price:
        repo.add_price_history(ocean.ocean_id, ocean.current_price)


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
        ocean_repository = OceanRepository(db)
        oceans = db.query(Ocean).all()

        # 전체 해양 관련 뉴스를 한 번에 검색
        try:
            async with httpx.AsyncClient() as client:
                # 부산 지역 해양 관련 의미있는 키워드로 검색
                query_keywords = (
                    "(부산 OR 해운대 OR 광안리 OR 송정 OR 영도 OR 다대포 OR 기장 OR 오륙도 OR 수영만 OR 부산항) "
                    "AND "
                    "(해양 OR 수질 OR 바다 OR 해수욕장 OR 해양오염 OR 해양환경 OR 해양보호 OR "
                    "수질개선 OR 해양쓰레기 OR 해양생태 OR 해양보전 OR 적조 OR 녹조 OR "
                    "해양관리 OR 수산 OR 어업 OR 해양생물 OR 해수 OR 연안)"
                )

                response = await client.get(
                    settings.NEWS_API_URL,
                    params={
                        "apiKey": settings.NEWS_API_KEY,
                        "q": query_keywords,
                        "language": "ko",
                        "sortBy": "publishedAt",
                        "pageSize": 100  # 더 많은 기사 가져오기
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    print(f"뉴스 API 오류: HTTP {response.status_code}")
                    return

                data = response.json()
                articles_data = data.get("articles", [])

                print(f"📰 뉴스 API에서 {len(articles_data)}개 기사 조회 완료")

                matched_count = 0
                for article_data in articles_data:
                    url = article_data.get("url")
                    title = article_data.get("title") or ""
                    description = article_data.get("description", "")
                    content = article_data.get("content", "")
                    image_url = article_data.get("urlToImage")

                    if not url or not title:
                        continue

                    # 이미 저장된 기사인지 확인
                    existing = db.query(Article).filter(Article.url == url).first()
                    if existing:
                        continue

                    # 제목과 내용에서 해양 이름 매칭 확인
                    matched_ocean = None
                    matched_keyword = None
                    full_text = (title + " " + description).lower()

                    # 해양 관련 키워드가 있는지 먼저 확인 (필터링)
                    ocean_keywords = ["해양", "바다", "수질", "해수욕장", "해안", "연안", "항구", "어업", "수산"]
                    has_ocean_context = any(kw in full_text for kw in ocean_keywords)

                    if not has_ocean_context:
                        # 해양과 무관한 기사는 스킵
                        continue

                    # 각 해양에 대해 키워드 매칭 시도
                    for ocean in oceans:
                        # 해양 이름에서 키워드 추출
                        ocean_name_clean = ocean.ocean_name.replace(" 앞바다", "").replace(" 해역", "").strip()

                        # 여러 키워드 생성
                        keywords = []

                        # 1. 전체 해양 이름
                        keywords.append(ocean.ocean_name)

                        # 2. 공백 제거한 이름
                        keywords.append(ocean_name_clean)

                        # 3. 공백으로 분리된 각 단어 (3글자 이상만)
                        if " " in ocean_name_clean:
                            for word in ocean_name_clean.split():
                                if len(word) >= 3:  # 3글자 이상만
                                    keywords.append(word)

                        # 키워드가 제목이나 내용에 있는지 확인
                        for keyword in keywords:
                            if keyword in full_text:
                                matched_ocean = ocean
                                matched_keyword = keyword
                                break

                        if matched_ocean:
                            break

                    # 매칭되는 해양이 없으면 스킵
                    if not matched_ocean:
                        continue

                    matched_count += 1
                    print(f"  ✅ 기사 매칭: [{matched_ocean.ocean_name}] 키워드: '{matched_keyword}' | {title[:40]}...")

                    # 기사 내용 준비 (description이나 content 사용)
                    article_content = description or content or ""

                    # AI로 감성 분석
                    sentiment_str = await ai_client.analyze_article_sentiment(
                        ocean_name=matched_ocean.ocean_name,
                        article_title=title,
                        article_content=article_content
                    )

                    # 문자열을 Enum으로 변환
                    if sentiment_str == "positive":
                        sentiment = ArticleSentiment.POSITIVE
                    elif sentiment_str == "negative":
                        sentiment = ArticleSentiment.NEGATIVE
                    else:
                        sentiment = ArticleSentiment.NEUTRAL

                    # 가격 변동량 계산
                    price_change = 0
                    if sentiment == ArticleSentiment.POSITIVE:
                        price_change = 150  # 긍정 기사: +150
                    elif sentiment == ArticleSentiment.NEGATIVE:
                        price_change = -150  # 부정 기사: -150

                    # 기사 저장 (content 필드 제외 - DB에 컬럼 없음)
                    new_article = Article(
                        ocean_id=matched_ocean.ocean_id,
                        ocean_name=matched_ocean.ocean_name,
                        title=title,
                        # content=article_content,  # 임시 제거
                        url=url,
                        image_url=image_url,
                        sentiment=sentiment,
                        price_change=price_change
                    )
                    db.add(new_article)

                    # 해양 시세 업데이트
                    previous_price = matched_ocean.current_price
                    matched_ocean.current_price += price_change
                    if matched_ocean.current_price < 100:  # 최소 가격 보장
                        matched_ocean.current_price = 100
                    _record_ocean_price_history(ocean_repository, matched_ocean, previous_price)

                db.commit()
                print(f"✅ 총 {matched_count}개 기사 매칭 및 저장 완료")

        except Exception as e:
            print(f"기사 수집 오류: {e}")
            db.rollback()

    except Exception as e:
        print(f"기사 수집 작업 오류: {e}")
        db.rollback()
    finally:
        db.close()


# 기존 키워드 기반 감성 분석 함수 (사용 안 함 - Gemini AI로 대체)
# def analyze_article_sentiment(title: str, content: str) -> ArticleSentiment:
#     """
#     기사 제목과 내용을 기반으로 감성 분석 (키워드 기반)
#     """
#     positive_keywords = ["보존", "개선", "깨끗", "회복", "성공", ...]
#     negative_keywords = ["오염", "위험", "감소", "파괴", "악화", ...]
#     ...
#     현재는 Gemini AI를 사용하여 더 정확한 감성 분석을 수행합니다.


async def update_ocean_prices_by_garbage():
    """
    쓰레기 수집 횟수에 따라 해양 시세를 업데이트합니다.

    - 쓰레기 수집이 많을수록 시세 상승
    - 쓰레기 수집이 적으면 시세 하락
    - 일정 기간 동안 쓰레기 수집이 부족하면 강제 경매
    """
    db: Session = SessionLocal()

    try:
        ocean_repository = OceanRepository(db)
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

            previous_price = ocean.current_price
            ocean.current_price += price_change
            if ocean.current_price < 100:
                ocean.current_price = 100
            _record_ocean_price_history(ocean_repository, ocean, previous_price)

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

    10초마다 실행되며, 각 건물의 수익률에 따라 소유자에게 크레딧을 지급합니다.
    """
    db: Session = SessionLocal()

    try:
        # 모든 건물 조회
        buildings = db.query(Building).all()

        if not buildings:
            # 건물이 없으면 조용히 종료
            return

        now = datetime.utcnow()
        total_income_distributed = 0
        initialized_count = 0
        income_count = 0

        print(f"\n🏢 빌딩 수익금 지급 시작 ({len(buildings)}개 건물 확인)")

        for building in buildings:
            # 마지막 수익금 지급 시간이 없으면 현재 시간으로 초기화
            if building.last_income_generated_at is None:
                building.last_income_generated_at = now
                initialized_count += 1
                print(f"  🆕 빌딩 ID {building.id} (소유자: {building.user_id}): 수익금 지급 시간 초기화")
                continue

            # 마지막 수익금 지급 이후 경과 시간 계산 (초 단위)
            elapsed_seconds = (now - building.last_income_generated_at).total_seconds()

            if elapsed_seconds >= 1:  # 1초 이상 경과
                # 수익금 계산
                income = int(elapsed_seconds) * building.income_rate

                # 소유자에게 크레딧 지급
                owner = db.query(User).filter(User.user_id == building.user_id).first()
                if owner:
                    old_credits = owner.credits
                    owner.credits += income
                    total_income_distributed += income
                    income_count += 1
                    building_type_name = "가게" if building.building_type == BuildingType.STORE else "빌딩"
                    print(f"  💰 {building_type_name} ID {building.id} (소유자: {building.user_id}): "
                          f"{income:,} 크레딧 지급 (경과: {int(elapsed_seconds)}초, "
                          f"수익률: {building.income_rate}/초, {old_credits:,} → {owner.credits:,})")
                else:
                    print(f"  ⚠️  빌딩 ID {building.id}: 소유자 {building.user_id}를 찾을 수 없습니다.")

                # 마지막 수익금 지급 시간 업데이트
                building.last_income_generated_at = now

        db.commit()

        if income_count > 0 or initialized_count > 0:
            print(f"✅ 수익금 지급 완료: 총 {total_income_distributed:,} 크레딧 지급 "
                  f"({income_count}개 건물, {initialized_count}개 초기화)\n")

    except Exception as e:
        print(f"❌ 수익금 지급 오류: {e}")
        import traceback
        traceback.print_exc()
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
            ocean_repository = OceanRepository(db)
            oceans = db.query(Ocean).all()
            print(f"🌊 {len(oceans)}개 해양에 대해 관측소 매칭 중...")

            matched_ocean_count = 0
            for ocean in oceans:
                # 해양과 가장 가까운 관측소 찾기
                closest_station = None
                min_distance = float('inf')

                for station in stations:
                    try:
                        station_lat = float(station.get("위도", 0))
                        station_lon = float(station.get("경도", 0))

                        # 거리 계산 (유클리드 거리 -> km로 변환)
                        # 위도/경도 1도 = 약 111km
                        distance = math.sqrt(
                            ((ocean.lat - station_lat) * 111) ** 2 +
                            ((ocean.lon - station_lon) * 111) ** 2
                        )

                        if distance < min_distance:
                            min_distance = distance
                            closest_station = station
                    except (ValueError, TypeError):
                        continue

                if closest_station and min_distance < 200:  # 200km 이내로 범위 확대
                    matched_ocean_count += 1
                    station_name = closest_station.get("관측소 명", "알 수 없음")
                    ocean_name_display = ocean.ocean_name if ocean.ocean_name else "이름없음"
                    print(f"  ✅ [{ocean_name_display}] 관측소 매칭: {station_name} (거리: {min_distance:.1f}km)")

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
                    previous_price = ocean.current_price
                    ocean.current_price += price_change
                    if ocean.current_price < 100:
                        ocean.current_price = 100
                    _record_ocean_price_history(ocean_repository, ocean, previous_price)

                    # 수질 데이터 업데이트 (관측소 정보 기반)
                    water_quality = db.query(WaterQuality).filter(
                        WaterQuality.ocean_id == ocean.ocean_id
                    ).first()

                    # 거리와 관측소 유형에 따라 수질 값 다르게 생성
                    # 거리가 가까울수록, 좋은 관측소일수록 더 좋은 수질
                    distance_factor = max(0.5, 1 - (min_distance / 200))  # 0.5 ~ 1.0

                    if "종합해양과학기지" in station_type:
                        quality_factor = 1.0
                    elif "해양관측부이" in station_type:
                        quality_factor = 0.9
                    elif "조위관측소" in station_type:
                        quality_factor = 0.8
                    else:
                        quality_factor = 0.7

                    # 해양별로 약간씩 다른 수질 값 생성
                    random.seed(ocean.ocean_id + int(min_distance * 10))  # 해양 ID와 거리로 시드 설정

                    base_do = 7.0 + (quality_factor * distance_factor * 2.0)  # 7.0 ~ 9.0
                    do_value = round(base_do + random.uniform(-0.5, 0.5), 1)

                    base_ph = 7.8 + (quality_factor * distance_factor * 0.5)  # 7.8 ~ 8.3
                    ph_value = round(base_ph + random.uniform(-0.2, 0.2), 1)

                    base_nitrogen = 0.5 - (quality_factor * distance_factor * 0.3)  # 0.2 ~ 0.5
                    nitrogen_value = round(base_nitrogen + random.uniform(-0.05, 0.05), 2)

                    base_phosphorus = 0.04 - (quality_factor * distance_factor * 0.02)  # 0.02 ~ 0.04
                    phosphorus_value = round(base_phosphorus + random.uniform(-0.005, 0.005), 3)

                    base_turbidity = 3.0 - (quality_factor * distance_factor * 2.0)  # 1.0 ~ 3.0
                    turbidity_value = round(base_turbidity + random.uniform(-0.3, 0.3), 1)

                    # 상태 판단
                    do_status = WaterQualityStatus.NORMAL if do_value >= 7.0 else WaterQualityStatus.WARNING
                    ph_status = WaterQualityStatus.NORMAL if 7.5 <= ph_value <= 8.5 else WaterQualityStatus.WARNING
                    nitrogen_status = WaterQualityStatus.NORMAL if nitrogen_value < 0.4 else WaterQualityStatus.WARNING
                    phosphorus_status = WaterQualityStatus.NORMAL if phosphorus_value < 0.03 else WaterQualityStatus.WARNING
                    turbidity_status = WaterQualityStatus.NORMAL if turbidity_value < 2.0 else WaterQualityStatus.WARNING

                    if not water_quality:
                        # 새로운 수질 데이터 생성 (관측소별로 다른 값)
                        water_quality = WaterQuality(
                            ocean_id=ocean.ocean_id,
                            dissolved_oxygen_value=do_value,
                            dissolved_oxygen_status=do_status,
                            ph_value=ph_value,
                            ph_status=ph_status,
                            nitrogen_value=nitrogen_value,
                            nitrogen_status=nitrogen_status,
                            phosphorus_value=phosphorus_value,
                            phosphorus_status=phosphorus_status,
                            turbidity_value=turbidity_value,
                            turbidity_status=turbidity_status,
                            heavy_metals_detected=0,
                            oil_spill_detected=0,
                            price_change=price_change
                        )
                        db.add(water_quality)
                        print(f"    💧 수질: DO={do_value}, pH={ph_value}, 질소={nitrogen_value}, 탁도={turbidity_value}")
                    else:
                        # 기존 수질 데이터 업데이트 (값 변경)
                        water_quality.dissolved_oxygen_value = do_value
                        water_quality.dissolved_oxygen_status = do_status
                        water_quality.ph_value = ph_value
                        water_quality.ph_status = ph_status
                        water_quality.nitrogen_value = nitrogen_value
                        water_quality.nitrogen_status = nitrogen_status
                        water_quality.phosphorus_value = phosphorus_value
                        water_quality.phosphorus_status = phosphorus_status
                        water_quality.turbidity_value = turbidity_value
                        water_quality.turbidity_status = turbidity_status
                        water_quality.price_change += price_change
                        water_quality.measured_at = datetime.utcnow()
                        print(f"    💧 수질 업데이트: DO={do_value}, pH={ph_value}")

            db.commit()
            print(f"✅ 해양 관측소 데이터 업데이트 완료: {matched_ocean_count}/{len(oceans)}개 해양에 수질 데이터 추가")

    except Exception as e:
        print(f"해양 관측소 데이터 수집 오류: {e}")
        db.rollback()
    finally:
        db.close()


async def finalize_expired_auctions():
    """
    종료 시간이 지난 경매를 자동으로 종료하고 크레딧을 이동합니다.

    1. end_time이 지난 ACTIVE 상태의 경매를 찾습니다.
    2. 입찰이 있는 경매만 종료 처리합니다.
    3. 최고 입찰자에게 크레딧을 차감하고 판매자에게 지급합니다.
    4. 소유권을 최고 입찰자에게 이전합니다.
    5. 경매 상태를 SOLD로 변경합니다.
    """
    db: Session = SessionLocal()

    try:
        from app.domain.ocean_trade.domain.repository import OceanTradeRepository
        from app.domain.ocean_trade.domain.entity import AuctionStatus
        from app.domain.auth.domain.repository import UserRepository

        repository = OceanTradeRepository(db)
        user_repository = UserRepository(db)

        # 종료 시간이 지난 경매 조회
        expired_auctions = repository.find_expired_auctions()

        for auction in expired_auctions:
            try:
                # 최고 입찰 조회
                highest_bid = repository.find_highest_bid(auction.id)

                if not highest_bid:
                    # 입찰이 없으면 경매 취소 처리 및 소유권 복구
                    auction.status = AuctionStatus.CANCELLED
                    auction.ended_at = datetime.now()

                    # 소유권 복구
                    ownership = repository.find_ownership_by_user_and_ocean(
                        auction.seller_id, auction.ocean_id
                    )
                    if ownership:
                        repository.update_ownership_square_meters(
                            ownership, ownership.square_meters + auction.square_meters
                        )
                    else:
                        repository.create_ownership(
                            user_id=auction.seller_id,
                            ocean_id=auction.ocean_id,
                            square_meters=auction.square_meters
                        )

                    print(f"⚠️ 경매 {auction.id}: 입찰이 없어 취소 처리되었습니다.")
                    continue

                # 크레딧 처리
                bidder = user_repository.find_by_username(highest_bid.bidder_id)
                seller = user_repository.find_by_username(auction.seller_id)

                if bidder:
                    bidder.credits -= highest_bid.bid_amount
                if seller:
                    seller.credits += highest_bid.bid_amount

                # 소유권 이전
                ownership = repository.find_ownership_by_user_and_ocean(
                    highest_bid.bidder_id, auction.ocean_id
                )
                if ownership:
                    repository.update_ownership_square_meters(
                        ownership, ownership.square_meters + auction.square_meters
                    )
                else:
                    repository.create_ownership(
                        user_id=highest_bid.bidder_id,
                        ocean_id=auction.ocean_id,
                        square_meters=auction.square_meters
                    )

                # 경매 상태 업데이트
                auction.status = AuctionStatus.SOLD
                auction.winner_id = highest_bid.bidder_id
                auction.ended_at = datetime.now()

                print(f"✅ 경매 {auction.id} 자동 종료: 낙찰자 {highest_bid.bidder_id}, 금액 {highest_bid.bid_amount}")

            except Exception as e:
                print(f"경매 {auction.id} 종료 처리 오류: {e}")
                continue

        db.commit()

    except Exception as e:
        print(f"경매 자동 종료 작업 오류: {e}")
        db.rollback()
    finally:
        db.close()
