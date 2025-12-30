from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.domain.ocean_trade.domain.entity import OceanSale, OceanAuction, AuctionBid, SaleStatus, AuctionStatus
from app.domain.ocean.domain.entity import Ocean
from app.domain.ocean_management.domain.entity import OceanOwnership


class OceanTradeRepository:
    """해양 거래 Repository"""

    def __init__(self, db: Session):
        self.db = db

    # Ocean 조회
    def find_ocean_by_id(self, ocean_id: int) -> Optional[Ocean]:
        """해양 ID로 해양을 조회합니다."""
        return self.db.query(Ocean).filter(Ocean.ocean_id == ocean_id).first()

    def find_all_oceans(
        self,
        region: Optional[str] = None,
        detail: Optional[str] = None
    ) -> List[Ocean]:
        """구매 가능한 해양 목록을 조회합니다."""
        query = self.db.query(Ocean).filter(Ocean.available_square_meters > 0)

        if region:
            query = query.filter(Ocean.region == region)
        if detail:
            query = query.filter(Ocean.detail == detail)

        return query.all()

    # Ownership 관리
    def find_ownership_by_user_and_ocean(
        self, user_id: str, ocean_id: int
    ) -> Optional[OceanOwnership]:
        """사용자와 해양 ID로 소유권을 조회합니다."""
        return (
            self.db.query(OceanOwnership)
            .filter(
                OceanOwnership.user_id == user_id,
                OceanOwnership.ocean_id == ocean_id
            )
            .first()
        )

    def create_ownership(
        self, user_id: str, ocean_id: int, square_meters: int
    ) -> OceanOwnership:
        """새로운 소유권을 생성합니다."""
        ownership = OceanOwnership(
            user_id=user_id,
            ocean_id=ocean_id,
            square_meters=square_meters
        )
        self.db.add(ownership)
        self.db.commit()
        self.db.refresh(ownership)
        return ownership

    def update_ownership_square_meters(
        self, ownership: OceanOwnership, square_meters: int
    ) -> OceanOwnership:
        """소유권의 평수를 업데이트합니다."""
        ownership.square_meters = square_meters
        self.db.commit()
        self.db.refresh(ownership)
        return ownership

    # Ocean 평수 업데이트
    def update_ocean_available_square_meters(
        self, ocean: Ocean, available_square_meters: int
    ):
        """해양의 구매 가능한 평수를 업데이트합니다."""
        ocean.available_square_meters = available_square_meters
        self.db.commit()
        self.db.refresh(ocean)

    # Sale 관리
    def create_sale(
        self,
        ocean_id: int,
        seller_id: str,
        square_meters: int,
        price: int
    ) -> OceanSale:
        """판매를 등록합니다."""
        sale = OceanSale(
            ocean_id=ocean_id,
            seller_id=seller_id,
            square_meters=square_meters,
            price=price,
            status=SaleStatus.ACTIVE
        )
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def find_sale_by_id(self, sale_id: int) -> Optional[OceanSale]:
        """판매 ID로 판매를 조회합니다."""
        return self.db.query(OceanSale).filter(OceanSale.id == sale_id).first()

    def update_sale_status(
        self, sale: OceanSale, status: SaleStatus, buyer_id: Optional[str] = None
    ) -> OceanSale:
        """판매 상태를 업데이트합니다."""
        sale.status = status
        if buyer_id:
            sale.buyer_id = buyer_id
        self.db.commit()
        self.db.refresh(sale)
        return sale

    # Auction 관리
    def create_auction(
        self,
        ocean_id: int,
        seller_id: str,
        square_meters: int,
        starting_price: int,
        end_time: datetime
    ) -> OceanAuction:
        """경매를 등록합니다."""
        auction = OceanAuction(
            ocean_id=ocean_id,
            seller_id=seller_id,
            square_meters=square_meters,
            starting_price=starting_price,
            current_price=starting_price,
            status=AuctionStatus.ACTIVE,
            end_time=end_time
        )
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        return auction

    def find_auction_by_id(self, auction_id: int) -> Optional[OceanAuction]:
        """경매 ID로 경매를 조회합니다."""
        return self.db.query(OceanAuction).filter(OceanAuction.id == auction_id).first()

    def find_active_auctions(
        self,
        region: Optional[str] = None,
        detail: Optional[str] = None
    ) -> List[OceanAuction]:
        """활성 경매 목록을 조회합니다."""
        query = (
            self.db.query(OceanAuction)
            .join(Ocean, OceanAuction.ocean_id == Ocean.ocean_id)
            .filter(OceanAuction.status == AuctionStatus.ACTIVE)
        )

        if region:
            query = query.filter(Ocean.region == region)
        if detail:
            query = query.filter(Ocean.detail == detail)

        return query.all()

    def find_expired_auctions(self) -> List[OceanAuction]:
        """종료 시간이 지난 활성 경매 목록을 조회합니다."""
        now = datetime.now()
        return (
            self.db.query(OceanAuction)
            .filter(
                OceanAuction.status == AuctionStatus.ACTIVE,
                OceanAuction.end_time <= now
            )
            .all()
        )

    def update_auction_current_price(
        self, auction: OceanAuction, current_price: int
    ) -> OceanAuction:
        """경매의 현재 최고가를 업데이트합니다."""
        auction.current_price = current_price
        self.db.commit()
        self.db.refresh(auction)
        return auction

    def update_auction_status(
        self, auction: OceanAuction, status: AuctionStatus, winner_id: Optional[str] = None
    ) -> OceanAuction:
        """경매 상태를 업데이트합니다."""
        auction.status = status
        if winner_id:
            auction.winner_id = winner_id
        self.db.commit()
        self.db.refresh(auction)
        return auction

    # Bid 관리
    def create_bid(
        self, auction_id: int, bidder_id: str, bid_amount: int
    ) -> AuctionBid:
        """입찰을 생성합니다."""
        bid = AuctionBid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            bid_amount=bid_amount
        )
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        return bid

    def find_highest_bid(self, auction_id: int) -> Optional[AuctionBid]:
        """경매의 최고 입찰을 조회합니다."""
        return (
            self.db.query(AuctionBid)
            .filter(AuctionBid.auction_id == auction_id)
            .order_by(AuctionBid.bid_amount.desc())
            .first()
        )
