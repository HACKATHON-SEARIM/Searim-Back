from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.database import Base


class SaleStatus(str, enum.Enum):
    """판매 상태 Enum"""
    ACTIVE = "ACTIVE"  # 판매 중
    SOLD = "SOLD"  # 판매 완료
    CANCELLED = "CANCELLED"  # 취소됨


class OceanSale(Base):
    """해양 판매 Entity"""

    __tablename__ = "ocean_sales"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="판매 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")
    seller_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="판매자 ID")
    square_meters = Column(Integer, nullable=False, comment="판매 평수")
    price = Column(Integer, nullable=False, comment="판매 가격")
    status = Column(SQLEnum(SaleStatus), default=SaleStatus.ACTIVE, nullable=False, comment="판매 상태")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="등록 일시")
    sold_at = Column(DateTime(timezone=True), nullable=True, comment="판매 완료 일시")
    buyer_id = Column(String(50), ForeignKey("users.user_id"), nullable=True, comment="구매자 ID")

    def __repr__(self):
        return f"<OceanSale(id={self.id}, ocean_id={self.ocean_id}, status={self.status})>"


class AuctionStatus(str, enum.Enum):
    """경매 상태 Enum"""
    ACTIVE = "ACTIVE"  # 경매 중
    SOLD = "SOLD"  # 낙찰 완료
    CANCELLED = "CANCELLED"  # 취소됨


class OceanAuction(Base):
    """해양 경매 Entity"""

    __tablename__ = "ocean_auctions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="경매 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")
    seller_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="판매자 ID")
    square_meters = Column(Integer, nullable=False, comment="경매 평수")
    starting_price = Column(Integer, nullable=False, comment="시작 가격 (현재 시세의 80%)")
    current_price = Column(Integer, nullable=False, comment="현재 최고 입찰가")
    status = Column(SQLEnum(AuctionStatus), default=AuctionStatus.ACTIVE, nullable=False, comment="경매 상태")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="등록 일시")
    end_time = Column(DateTime(timezone=True), nullable=False, comment="경매 종료 예정 시간 (등록 후 10분)")
    ended_at = Column(DateTime(timezone=True), nullable=True, comment="경매 종료 일시")
    winner_id = Column(String(50), ForeignKey("users.user_id"), nullable=True, comment="낙찰자 ID")

    def __repr__(self):
        return f"<OceanAuction(id={self.id}, ocean_id={self.ocean_id}, status={self.status})>"


class AuctionBid(Base):
    """경매 입찰 기록 Entity"""

    __tablename__ = "auction_bids"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="입찰 ID")
    auction_id = Column(Integer, ForeignKey("ocean_auctions.id"), nullable=False, index=True, comment="경매 ID")
    bidder_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True, comment="입찰자 ID")
    bid_amount = Column(Integer, nullable=False, comment="입찰 금액")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="입찰 일시")

    def __repr__(self):
        return f"<AuctionBid(id={self.id}, auction_id={self.auction_id}, amount={self.bid_amount})>"
