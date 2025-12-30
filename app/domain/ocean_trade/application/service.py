from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from app.domain.ocean_trade.domain.repository import OceanTradeRepository
from app.domain.ocean.domain.repository import OceanRepository
from app.domain.ocean_trade.domain.entity import (
    OceanSale,
    OceanAuction,
    AuctionBid,
    SaleStatus,
    AuctionStatus
)
from app.domain.ocean.domain.entity import Ocean
from app.domain.ocean_management.domain.entity import OceanOwnership
from app.domain.auth.domain.repository import UserRepository


class OceanTradeService:
    """해양 거래 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = OceanTradeRepository(db)
        self.ocean_repository = OceanRepository(db)
        self.user_repository = UserRepository(db)

    def get_purchasable_oceans(
        self,
        region: str = None,
        detail: str = None
    ) -> List[Ocean]:
        """구매 가능한 해양 목록을 조회합니다."""
        return self.repository.find_all_oceans(region=region, detail=detail)

    def get_auctionable_oceans(
        self,
        region: str = None,
        detail: str = None
    ) -> List[Ocean]:
        """경매 가능한 해양 목록을 조회합니다."""
        auctions = self.repository.find_active_auctions(region=region, detail=detail)
        ocean_ids = [auction.ocean_id for auction in auctions]

        # 중복 제거하고 Ocean 정보 조회
        unique_ocean_ids = list(set(ocean_ids))
        oceans = []
        for ocean_id in unique_ocean_ids:
            ocean = self.repository.find_ocean_by_id(ocean_id)
            if ocean:
                oceans.append(ocean)

        return oceans

    def get_recent_price_history(
        self,
        ocean_ids: List[int],
        limit: int = 10
    ) -> Dict[int, List[int]]:
        """해양별 최근 시세 목록을 조회합니다."""
        return self.ocean_repository.find_recent_prices_by_ocean_ids(
            ocean_ids=ocean_ids,
            limit=limit
        )

    def purchase_ocean(
        self,
        ocean_id: int,
        username: str,
        square_meters: int
    ) -> OceanOwnership:
        """해양을 구매합니다."""
        # 해양 존재 여부 확인
        ocean = self.repository.find_ocean_by_id(ocean_id)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해양 ID {ocean_id}를 찾을 수 없습니다."
            )

        # 구매 가능한 평수 확인
        if ocean.available_square_meters < square_meters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"구매 가능한 평수가 부족합니다. (가능: {ocean.available_square_meters}평)"
            )

        # 사용자 크레딧 확인
        user = self.user_repository.find_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        total_cost = ocean.current_price * square_meters
        if user.credits < total_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"크레딧이 부족합니다. (필요: {total_cost}, 보유: {user.credits})"
            )

        # 크레딧 차감
        user.credits -= total_cost
        self.db.commit()

        # 해양 가용 평수 감소
        self.repository.update_ocean_available_square_meters(
            ocean, ocean.available_square_meters - square_meters
        )

        # 소유권 생성 또는 업데이트
        ownership = self.repository.find_ownership_by_user_and_ocean(username, ocean_id)
        if ownership:
            ownership = self.repository.update_ownership_square_meters(
                ownership, ownership.square_meters + square_meters
            )
        else:
            ownership = self.repository.create_ownership(
                user_id=username,
                ocean_id=ocean_id,
                square_meters=square_meters
            )

        return ownership

    def register_sale(
        self,
        ocean_id: int,
        seller_username: str,
        square_meters: int
    ) -> OceanSale:
        """해양 판매를 등록합니다. 판매 가격은 DB에 저장된 해양의 현재 가격을 사용합니다."""
        # 해양 존재 여부 확인
        ocean = self.repository.find_ocean_by_id(ocean_id)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해양 ID {ocean_id}를 찾을 수 없습니다."
            )

        # 소유권 확인
        ownership = self.repository.find_ownership_by_user_and_ocean(
            seller_username, ocean_id
        )
        if not ownership or ownership.square_meters < square_meters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"판매할 소유권이 부족합니다."
            )

        # DB에 저장된 해양의 현재 가격 사용 (1평당 가격)
        price_per_square = ocean.current_price

        # 판매 등록
        sale = self.repository.create_sale(
            ocean_id=ocean_id,
            seller_id=seller_username,
            square_meters=square_meters,
            price=price_per_square
        )

        # 판매 등록 시 소유권 차감
        self.repository.update_ownership_square_meters(
            ownership, ownership.square_meters - square_meters
        )

        # 해양을 판매하면 해당 해양의 건물 삭제
        deleted_buildings = self.repository.delete_buildings_by_user_and_ocean(
            seller_username, ocean_id
        )
        if deleted_buildings > 0:
            print(f"🏚️  해양 판매로 인해 {deleted_buildings}개 건물 삭제 (사용자: {seller_username}, 해양: {ocean_id})")

        return sale

    def register_auction(
        self,
        ocean_id: int,
        seller_username: str,
        square_meters: int
    ) -> OceanAuction:
        """해양 경매를 등록합니다."""
        # 해양 존재 여부 확인
        ocean = self.repository.find_ocean_by_id(ocean_id)
        if not ocean:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해양 ID {ocean_id}를 찾을 수 없습니다."
            )

        # 소유권 확인
        ownership = self.repository.find_ownership_by_user_and_ocean(
            seller_username, ocean_id
        )
        if not ownership or ownership.square_meters < square_meters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"경매에 올릴 소유권이 부족합니다."
            )

        # 시작 가격 계산 (현재 시세의 80%)
        starting_price = int(ocean.current_price * square_meters * 0.8)

        # 경매 종료 시간 계산 (10분 후)
        end_time = datetime.now() + timedelta(minutes=10)

        # 경매 등록
        auction = self.repository.create_auction(
            ocean_id=ocean_id,
            seller_id=seller_username,
            square_meters=square_meters,
            starting_price=starting_price,
            end_time=end_time
        )

        # 경매 등록 시 소유권 차감
        self.repository.update_ownership_square_meters(
            ownership, ownership.square_meters - square_meters
        )

        # 해양을 경매에 올리면 해당 해양의 건물 삭제
        deleted_buildings = self.repository.delete_buildings_by_user_and_ocean(
            seller_username, ocean_id
        )
        if deleted_buildings > 0:
            print(f"🏚️  해양 경매로 인해 {deleted_buildings}개 건물 삭제 (사용자: {seller_username}, 해양: {ocean_id})")

        return auction

    def purchase_from_sale(
        self,
        sale_id: int,
        buyer_username: str
    ) -> Tuple[OceanOwnership, OceanSale]:
        """판매 등록된 해양을 구매합니다."""
        # 판매 조회
        sale = self.repository.find_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"판매 ID {sale_id}를 찾을 수 없습니다."
            )

        if sale.status != SaleStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 판매가 완료되었거나 취소된 상태입니다."
            )

        if sale.seller_id == buyer_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자신이 등록한 판매는 구매할 수 없습니다."
            )

        # 사용자 크레딧 확인
        buyer = self.user_repository.find_by_username(buyer_username)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="구매자를 찾을 수 없습니다."
            )

        total_cost = sale.price * sale.square_meters
        if buyer.credits < total_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"크레딧이 부족합니다. (필요: {total_cost}, 보유: {buyer.credits})"
            )

        # 크레딧 처리
        buyer.credits -= total_cost
        seller = self.user_repository.find_by_username(sale.seller_id)
        if seller:
            seller.credits += total_cost

        self.db.commit()

        # 소유권 이전
        ownership = self.repository.find_ownership_by_user_and_ocean(
            buyer_username, sale.ocean_id
        )
        if ownership:
            ownership = self.repository.update_ownership_square_meters(
                ownership, ownership.square_meters + sale.square_meters
            )
        else:
            ownership = self.repository.create_ownership(
                user_id=buyer_username,
                ocean_id=sale.ocean_id,
                square_meters=sale.square_meters
            )

        # 판매 상태 업데이트
        sale = self.repository.update_sale_status(
            sale, SaleStatus.SOLD, buyer_id=buyer_username
        )

        return ownership, sale

    def bid_on_auction(
        self,
        auction_id: int,
        bidder_username: str,
        bid_amount: int
    ) -> AuctionBid:
        """경매에 입찰합니다."""
        # 경매 조회
        auction = self.repository.find_auction_by_id(auction_id)
        if not auction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"경매 ID {auction_id}를 찾을 수 없습니다."
            )

        if auction.status != AuctionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="경매가 종료되었거나 취소된 상태입니다."
            )

        if auction.seller_id == bidder_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자신이 등록한 경매에는 입찰할 수 없습니다."
            )

        # 입찰 금액 검증
        if bid_amount <= auction.current_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"입찰 금액은 현재 최고가({auction.current_price})보다 높아야 합니다."
            )

        # 사용자 크레딧 확인
        bidder = self.user_repository.find_by_username(bidder_username)
        if not bidder or bidder.credits < bid_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="크레딧이 부족합니다."
            )

        # 입찰 생성
        bid = self.repository.create_bid(
            auction_id=auction_id,
            bidder_id=bidder_username,
            bid_amount=bid_amount
        )

        # 경매 최고가 업데이트
        self.repository.update_auction_current_price(auction, bid_amount)

        return bid

    def finalize_auction(
        self,
        auction_id: int
    ) -> Tuple[OceanOwnership, OceanAuction]:
        """경매를 종료하고 낙찰자에게 소유권을 이전합니다."""
        # 경매 조회
        auction = self.repository.find_auction_by_id(auction_id)
        if not auction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"경매 ID {auction_id}를 찾을 수 없습니다."
            )

        if auction.status != AuctionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 종료되었거나 취소된 경매입니다."
            )

        # 최고 입찰 조회
        highest_bid = self.repository.find_highest_bid(auction_id)
        if not highest_bid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="입찰이 없는 경매는 종료할 수 없습니다."
            )

        # 크레딧 처리
        bidder = self.user_repository.find_by_username(highest_bid.bidder_id)
        seller = self.user_repository.find_by_username(auction.seller_id)

        if bidder:
            bidder.credits -= highest_bid.bid_amount
        if seller:
            seller.credits += highest_bid.bid_amount

        self.db.commit()

        # 소유권 이전
        ownership = self.repository.find_ownership_by_user_and_ocean(
            highest_bid.bidder_id, auction.ocean_id
        )
        if ownership:
            ownership = self.repository.update_ownership_square_meters(
                ownership, ownership.square_meters + auction.square_meters
            )
        else:
            ownership = self.repository.create_ownership(
                user_id=highest_bid.bidder_id,
                ocean_id=auction.ocean_id,
                square_meters=auction.square_meters
            )

        # 경매 상태 업데이트
        auction = self.repository.update_auction_status(
            auction, AuctionStatus.SOLD, winner_id=highest_bid.bidder_id
        )

        return ownership, auction
