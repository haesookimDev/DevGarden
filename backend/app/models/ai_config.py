import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIConfig(Base):
    __tablename__ = "ai_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'claude', 'openai', 'google', 'private'
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100))
    base_url: Mapped[str | None] = mapped_column(Text)  # For private models
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="ai_configs")


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    task_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'document', 'git', 'portfolio'
    status: Mapped[str] = mapped_column(String(20), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    input_data: Mapped[dict | None] = mapped_column(JSONB)
    result_post_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id"))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    result_post = relationship("Post")
