import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_current_user
from app.database import get_db
from app.models.ai_config import AIConfig, GenerationTask
from app.models.user import User
from app.schemas.ai import (
    GenerateFromDocumentRequest,
    GenerateFromGitRequest,
    GenerateFromPortfolioRequest,
    GenerationTaskResponse,
)
from app.ai.factory import AIProviderFactory
from app.services.encryption_service import decrypt_api_key

router = APIRouter()


async def _get_user_ai_provider(db: AsyncSession, user_id: uuid.UUID):
    """Get the user's default AI provider."""
    result = await db.execute(
        select(AIConfig).where(AIConfig.user_id == user_id, AIConfig.is_default == True, AIConfig.is_active == True)
    )
    config = result.scalar_one_or_none()

    if not config:
        # Fallback to any active config
        result = await db.execute(
            select(AIConfig).where(AIConfig.user_id == user_id, AIConfig.is_active == True)
        )
        config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No AI provider configured. Please add an AI provider in Settings.",
        )

    api_key = decrypt_api_key(config.api_key_encrypted)
    return AIProviderFactory.create(
        provider=config.provider,
        api_key=api_key,
        model_name=config.model_name,
        base_url=config.base_url,
    )


@router.post("/from-document", response_model=GenerationTaskResponse)
async def generate_from_document(
    request: GenerateFromDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start blog generation from an uploaded document."""
    # Verify AI provider is configured
    await _get_user_ai_provider(db, current_user.id)

    task = GenerationTask(
        user_id=current_user.id,
        task_type="document",
        status="pending",
        input_data={"file_url": request.file_url, "language": request.language},
    )
    db.add(task)
    await db.flush()

    # Trigger background task
    from app.worker.tasks import process_document_generation
    process_document_generation.delay(str(task.id))

    return GenerationTaskResponse.model_validate(task)


@router.post("/from-git", response_model=GenerationTaskResponse)
async def generate_from_git(
    request: GenerateFromGitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start blog generation from a Git repository."""
    await _get_user_ai_provider(db, current_user.id)

    task = GenerationTask(
        user_id=current_user.id,
        task_type="git",
        status="pending",
        input_data={
            "repo_url": request.repo_url,
            "access_token": request.access_token,
            "language": request.language,
        },
    )
    db.add(task)
    await db.flush()

    from app.worker.tasks import process_git_generation
    process_git_generation.delay(str(task.id))

    return GenerationTaskResponse.model_validate(task)


@router.post("/from-portfolio", response_model=GenerationTaskResponse)
async def generate_from_portfolio(
    request: GenerateFromPortfolioRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start blog generation from a portfolio item."""
    await _get_user_ai_provider(db, current_user.id)

    task = GenerationTask(
        user_id=current_user.id,
        task_type="portfolio",
        status="pending",
        input_data={"portfolio_item_id": str(request.portfolio_item_id), "language": request.language},
    )
    db.add(task)
    await db.flush()

    from app.worker.tasks import process_portfolio_generation
    process_portfolio_generation.delay(str(task.id))

    return GenerationTaskResponse.model_validate(task)


@router.get("/status/{task_id}", response_model=GenerationTaskResponse)
async def get_task_status(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check generation task status."""
    result = await db.execute(
        select(GenerationTask).where(GenerationTask.id == task_id, GenerationTask.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return GenerationTaskResponse.model_validate(task)


@router.get("/stream/{task_id}")
async def stream_generation(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream generation results via SSE."""
    import asyncio
    import json

    from redis.asyncio import Redis

    from app.config import settings

    # Verify task ownership
    result = await db.execute(
        select(GenerationTask).where(GenerationTask.id == task_id, GenerationTask.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    async def event_generator():
        redis = Redis.from_url(settings.redis_url)
        channel = f"generation:{task_id}"
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    if data.get("event") == "chunk":
                        yield {"event": "chunk", "data": data["content"]}
                    elif data.get("event") == "done":
                        yield {"event": "done", "data": json.dumps({"post_id": data.get("post_id")})}
                        break
                    elif data.get("event") == "error":
                        yield {"event": "error", "data": data.get("message", "Unknown error")}
                        break
        finally:
            await pubsub.unsubscribe(channel)
            await redis.close()

    return EventSourceResponse(event_generator())
