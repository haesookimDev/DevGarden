import uuid
from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    excerpt: str | None = None
    cover_image_url: str | None = None
    category: str | None = None
    tags: list[str] | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    excerpt: str | None = None
    cover_image_url: str | None = None
    category: str | None = None
    tags: list[str] | None = None


class PostResponse(PostBase):
    id: uuid.UUID
    user_id: uuid.UUID
    slug: str
    status: str
    source_type: str | None
    reading_time_min: int | None
    view_count: int
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    page: int
    per_page: int
