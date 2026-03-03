import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))  # 'tech', 'troubleshooting', 'project'
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    status: Mapped[str] = mapped_column(String(20), default="draft")  # 'draft', 'published'
    source_type: Mapped[str | None] = mapped_column(String(20))  # 'manual', 'document', 'git', 'portfolio'
    source_file_url: Mapped[str | None] = mapped_column(Text)
    reading_time_min: Mapped[int | None] = mapped_column(Integer)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", back_populates="posts")
    portfolio_links = relationship("PortfolioPostLink", back_populates="post", cascade="all, delete-orphan")
