import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.ai_config import AIConfig
from app.models.user import User
from app.schemas.ai import AIConfigCreate, AIConfigResponse, AIConfigUpdate
from app.schemas.user import UserResponse, UserUpdate
from app.services.encryption_service import encrypt_api_key

router = APIRouter()


@router.get("/ai", response_model=list[AIConfigResponse])
async def list_ai_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's AI provider configurations."""
    result = await db.execute(select(AIConfig).where(AIConfig.user_id == current_user.id))
    configs = result.scalars().all()
    return [AIConfigResponse.model_validate(c) for c in configs]


@router.post("/ai", response_model=AIConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_config(
    data: AIConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new AI provider configuration."""
    # If setting as default, unset other defaults
    if data.is_default:
        existing = await db.execute(
            select(AIConfig).where(AIConfig.user_id == current_user.id, AIConfig.is_default == True)
        )
        for config in existing.scalars():
            config.is_default = False

    config = AIConfig(
        user_id=current_user.id,
        provider=data.provider,
        api_key_encrypted=encrypt_api_key(data.api_key),
        model_name=data.model_name,
        base_url=data.base_url,
        is_default=data.is_default,
    )
    db.add(config)
    await db.flush()
    return AIConfigResponse.model_validate(config)


@router.put("/ai/{config_id}", response_model=AIConfigResponse)
async def update_ai_config(
    config_id: uuid.UUID,
    data: AIConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an AI provider configuration."""
    result = await db.execute(
        select(AIConfig).where(AIConfig.id == config_id, AIConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI config not found")

    update_data = data.model_dump(exclude_unset=True)
    if "api_key" in update_data and update_data["api_key"]:
        config.api_key_encrypted = encrypt_api_key(update_data.pop("api_key"))

    if update_data.get("is_default"):
        existing = await db.execute(
            select(AIConfig).where(AIConfig.user_id == current_user.id, AIConfig.is_default == True)
        )
        for c in existing.scalars():
            c.is_default = False

    for field, value in update_data.items():
        setattr(config, field, value)

    await db.flush()
    return AIConfigResponse.model_validate(config)


@router.delete("/ai/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an AI provider configuration."""
    result = await db.execute(
        select(AIConfig).where(AIConfig.id == config_id, AIConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI config not found")
    await db.delete(config)
    await db.flush()


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    return UserResponse.model_validate(current_user)
