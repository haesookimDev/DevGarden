import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'project', 'award', 'career'
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    tech_stack: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    organization: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[str | None] = mapped_column(String(200))
    source_url: Mapped[str | None] = mapped_column(Text)
    image_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolio_items")
    post_links = relationship("PortfolioPostLink", back_populates="portfolio_item", cascade="all, delete-orphan")


class PortfolioPostLink(Base):
    __tablename__ = "portfolio_post_links"

    portfolio_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("portfolio_items.id", ondelete="CASCADE"), primary_key=True
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )

    portfolio_item = relationship("PortfolioItem", back_populates="post_links")
    post = relationship("Post", back_populates="portfolio_links")
