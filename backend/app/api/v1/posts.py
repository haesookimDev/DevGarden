import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostListResponse, PostResponse, PostUpdate
from app.services import post_service

router = APIRouter()


@router.get("", response_model=PostListResponse)
async def list_posts(
    category: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List published posts with optional filtering."""
    posts, total = await post_service.get_posts(
        db, category=category, search=search, status="published", page=page, per_page=per_page
    )
    return PostListResponse(
        posts=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single post by slug."""
    post = await post_service.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return PostResponse.model_validate(post)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new blog post."""
    post = await post_service.create_post(db, current_user.id, data)
    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing post."""
    post = await post_service.get_post_by_id(db, post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post = await post_service.update_post(db, post, data)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a post."""
    post = await post_service.get_post_by_id(db, post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await post_service.delete_post(db, post)


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a draft post."""
    post = await post_service.get_post_by_id(db, post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post = await post_service.publish_post(db, post)
    return PostResponse.model_validate(post)
