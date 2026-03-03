import uuid
from datetime import date, datetime

from pydantic import BaseModel


class PortfolioItemBase(BaseModel):
    type: str  # 'project', 'award', 'career'
    title: str
    description: str | None = None
    tech_stack: list[str] | None = None
    start_date: date | None = None
    end_date: date | None = None
    organization: str | None = None
    role: str | None = None
    source_url: str | None = None
    image_urls: list[str] | None = None
    sort_order: int = 0


class PortfolioItemCreate(PortfolioItemBase):
    pass


class PortfolioItemUpdate(BaseModel):
    type: str | None = None
    title: str | None = None
    description: str | None = None
    tech_stack: list[str] | None = None
    start_date: date | None = None
    end_date: date | None = None
    organization: str | None = None
    role: str | None = None
    source_url: str | None = None
    image_urls: list[str] | None = None
    sort_order: int | None = None


class PortfolioItemResponse(PortfolioItemBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
