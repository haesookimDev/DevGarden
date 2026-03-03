import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


def _generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return f"{slug}-{uuid.uuid4().hex[:8]}"


def _estimate_reading_time(content: str) -> int:
    """Estimate reading time in minutes (200 words/min for mixed content)."""
    word_count = len(content.split())
    return max(1, word_count // 200)


async def create_post(db: AsyncSession, user_id: uuid.UUID, data: PostCreate) -> Post:
    post = Post(
        user_id=user_id,
        title=data.title,
        slug=_generate_slug(data.title),
        content=data.content,
        excerpt=data.excerpt,
        cover_image_url=data.cover_image_url,
        category=data.category,
        tags=data.tags,
        source_type="manual",
        reading_time_min=_estimate_reading_time(data.content),
    )
    db.add(post)
    await db.flush()
    return post


async def get_posts(
    db: AsyncSession,
    user_id: uuid.UUID | None = None,
    category: str | None = None,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    per_page: int = 12,
) -> tuple[list[Post], int]:
    query = select(Post)

    if user_id:
        query = query.where(Post.user_id == user_id)
    if category:
        query = query.where(Post.category == category)
    if status and status != "all":
        query = query.where(Post.status == status)
    elif not status:
        query = query.where(Post.status == "published")
    if search:
        query = query.where(Post.title.ilike(f"%{search}%") | Post.content.ilike(f"%{search}%"))

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Post.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    posts = list(result.scalars().all())

    return posts, total


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(select(Post).where(Post.slug == slug))
    return result.scalar_one_or_none()


async def get_post_by_id(db: AsyncSession, post_id: uuid.UUID) -> Post | None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def update_post(db: AsyncSession, post: Post, data: PostUpdate) -> Post:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    if "content" in update_data:
        post.reading_time_min = _estimate_reading_time(post.content)
    await db.flush()
    return post


async def delete_post(db: AsyncSession, post: Post):
    await db.delete(post)
    await db.flush()


async def publish_post(db: AsyncSession, post: Post) -> Post:
    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    await db.flush()
    return post
