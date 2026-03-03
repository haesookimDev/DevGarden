import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    bio: Mapped[str | None] = mapped_column(Text)
    github_url: Mapped[str | None] = mapped_column(String(500))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    portfolio_items = relationship("PortfolioItem", back_populates="user", cascade="all, delete-orphan")
    ai_configs = relationship("AIConfig", back_populates="user", cascade="all, delete-orphan")
