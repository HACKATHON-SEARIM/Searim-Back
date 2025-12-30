from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.database import Base


class ArticleSentiment(str, enum.Enum):
    """기사 감성 Enum"""
    POSITIVE = "positive"  # 긍정
    NEGATIVE = "negative"  # 부정
    NEUTRAL = "neutral"  # 중립


class Article(Base):
    """기사 Entity"""

    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True, autoincrement=True, comment="기사 ID")
    ocean_id = Column(Integer, ForeignKey("oceans.ocean_id"), nullable=False, index=True, comment="해양 ID")
    ocean_name = Column(String(100), nullable=False, comment="해양 이름")
    title = Column(String(500), nullable=False, comment="기사 제목")
    content = Column(String(2000), comment="기사 내용 (요약)")
    url = Column(String(500), nullable=False, unique=True, comment="기사 URL")
    image_url = Column(String(500), comment="기사 이미지 URL")
    sentiment = Column(
        SQLEnum(ArticleSentiment),
        default=ArticleSentiment.NEUTRAL,
        nullable=False,
        comment="기사 감성"
    )
    price_change = Column(Integer, default=0, comment="가격 변동량")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")

    def __repr__(self):
        return f"<Article(article_id={self.article_id}, ocean_id={self.ocean_id}, sentiment={self.sentiment})>"
