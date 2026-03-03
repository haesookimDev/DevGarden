import asyncio
import json
import uuid

import redis

from app.worker.celery_app import celery
from app.config import settings


def _get_redis():
    return redis.Redis.from_url(settings.redis_url)


def _publish(task_id: str, event: str, **kwargs):
    """Publish SSE event to Redis channel."""
    r = _get_redis()
    r.publish(f"generation:{task_id}", json.dumps({"event": event, **kwargs}))


def _run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(bind=True)
def process_document_generation(self, task_id: str):
    """Process document → blog generation."""
    _run_async(_async_process_document(task_id))


@celery.task(bind=True)
def process_git_generation(self, task_id: str):
    """Process git repo → blog generation."""
    _run_async(_async_process_git(task_id))


@celery.task(bind=True)
def process_portfolio_generation(self, task_id: str):
    """Process portfolio → blog generation."""
    _run_async(_async_process_portfolio(task_id))


async def _async_process_document(task_id: str):
    from datetime import datetime, timezone

    from sqlalchemy import select

    from app.database import async_session
    from app.models.ai_config import AIConfig, GenerationTask
    from app.ai.factory import AIProviderFactory
    from app.services.encryption_service import decrypt_api_key
    from app.services.storage_service import StorageService, BUCKET_DOCUMENTS
    from app.services.blog_generation_service import save_generated_post
    from app.parsers.pdf_parser import PDFParser
    from app.parsers.docx_parser import DOCXParser
    from app.parsers.pptx_parser import PPTXParser

    async with async_session() as db:
        try:
            # Get task
            result = await db.execute(select(GenerationTask).where(GenerationTask.id == uuid.UUID(task_id)))
            task = result.scalar_one()
            task.status = "processing"
            await db.commit()

            input_data = task.input_data
            file_url = input_data["file_url"]
            language = input_data.get("language", "ko")

            # Get AI provider
            ai_result = await db.execute(
                select(AIConfig).where(AIConfig.user_id == task.user_id, AIConfig.is_active == True)
                .order_by(AIConfig.is_default.desc())
            )
            ai_config = ai_result.scalar_one()
            api_key = decrypt_api_key(ai_config.api_key_encrypted)
            provider = AIProviderFactory.create(ai_config.provider, api_key, ai_config.model_name, ai_config.base_url)

            # Download and parse document
            storage = StorageService()
            bucket = file_url.split("/")[0]
            object_name = "/".join(file_url.split("/")[1:])
            file_data = storage.get_file(bucket, object_name)

            # Select parser
            if file_url.endswith(".pdf"):
                parser = PDFParser()
            elif file_url.endswith(".docx"):
                parser = DOCXParser()
            elif file_url.endswith(".pptx"):
                parser = PPTXParser()
            else:
                raise ValueError(f"Unsupported file type: {file_url}")

            parsed = parser.parse(file_data)
            filename = file_url.split("/")[-1]

            # Generate via streaming
            from app.services.blog_generation_service import generate_from_document
            full_response = ""
            async for chunk in generate_from_document(provider, parsed, filename, language):
                full_response += chunk
                _publish(task_id, "chunk", content=chunk)

            # Save post
            post = await save_generated_post(db, task.user_id, full_response, "document", file_url)
            task.status = "completed"
            task.result_post_id = post.id
            task.completed_at = datetime.now(timezone.utc)
            await db.commit()

            _publish(task_id, "done", post_id=str(post.id))

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()
            _publish(task_id, "error", message=str(e))


async def _async_process_git(task_id: str):
    from datetime import datetime, timezone

    from sqlalchemy import select

    from app.database import async_session
    from app.models.ai_config import AIConfig, GenerationTask
    from app.ai.factory import AIProviderFactory
    from app.services.encryption_service import decrypt_api_key
    from app.services.git_service import analyze_repository
    from app.services.blog_generation_service import save_generated_post

    async with async_session() as db:
        try:
            result = await db.execute(select(GenerationTask).where(GenerationTask.id == uuid.UUID(task_id)))
            task = result.scalar_one()
            task.status = "processing"
            await db.commit()

            input_data = task.input_data
            repo_url = input_data["repo_url"]
            access_token = input_data.get("access_token")
            language = input_data.get("language", "ko")

            # Get AI provider
            ai_result = await db.execute(
                select(AIConfig).where(AIConfig.user_id == task.user_id, AIConfig.is_active == True)
                .order_by(AIConfig.is_default.desc())
            )
            ai_config = ai_result.scalar_one()
            api_key = decrypt_api_key(ai_config.api_key_encrypted)
            provider = AIProviderFactory.create(ai_config.provider, api_key, ai_config.model_name, ai_config.base_url)

            # Analyze repo (sync, runs in worker)
            _publish(task_id, "chunk", content="Analyzing repository structure...\n\n")
            repo_analysis = analyze_repository(repo_url, access_token)

            # Generate via streaming
            from app.services.blog_generation_service import generate_from_git
            full_response = ""
            async for chunk in generate_from_git(provider, repo_analysis, language):
                full_response += chunk
                _publish(task_id, "chunk", content=chunk)

            post = await save_generated_post(db, task.user_id, full_response, "git")
            task.status = "completed"
            task.result_post_id = post.id
            task.completed_at = datetime.now(timezone.utc)
            await db.commit()

            _publish(task_id, "done", post_id=str(post.id))

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()
            _publish(task_id, "error", message=str(e))


async def _async_process_portfolio(task_id: str):
    from datetime import datetime, timezone

    from sqlalchemy import select

    from app.database import async_session
    from app.models.ai_config import AIConfig, GenerationTask
    from app.models.portfolio import PortfolioItem
    from app.ai.factory import AIProviderFactory
    from app.services.encryption_service import decrypt_api_key
    from app.services.blog_generation_service import save_generated_post
    from app.services.portfolio_service import link_post_to_portfolio

    async with async_session() as db:
        try:
            result = await db.execute(select(GenerationTask).where(GenerationTask.id == uuid.UUID(task_id)))
            task = result.scalar_one()
            task.status = "processing"
            await db.commit()

            input_data = task.input_data
            portfolio_item_id = uuid.UUID(input_data["portfolio_item_id"])
            language = input_data.get("language", "ko")

            # Get portfolio item
            item_result = await db.execute(select(PortfolioItem).where(PortfolioItem.id == portfolio_item_id))
            item = item_result.scalar_one()

            # Get AI provider
            ai_result = await db.execute(
                select(AIConfig).where(AIConfig.user_id == task.user_id, AIConfig.is_active == True)
                .order_by(AIConfig.is_default.desc())
            )
            ai_config = ai_result.scalar_one()
            api_key = decrypt_api_key(ai_config.api_key_encrypted)
            provider = AIProviderFactory.create(ai_config.provider, api_key, ai_config.model_name, ai_config.base_url)

            # Prepare data
            portfolio_data = {
                "type": item.type,
                "title": item.title,
                "description": item.description or "",
                "tech_stack": ", ".join(item.tech_stack or []),
                "organization": item.organization or "",
                "role": item.role or "",
                "start_date": str(item.start_date) if item.start_date else "N/A",
                "end_date": str(item.end_date) if item.end_date else "Present",
                "source_url": item.source_url or "N/A",
            }

            # Generate via streaming
            from app.services.blog_generation_service import generate_from_portfolio
            full_response = ""
            async for chunk in generate_from_portfolio(provider, portfolio_data, language):
                full_response += chunk
                _publish(task_id, "chunk", content=chunk)

            post = await save_generated_post(db, task.user_id, full_response, "portfolio")
            task.status = "completed"
            task.result_post_id = post.id
            task.completed_at = datetime.now(timezone.utc)
            await db.commit()

            # Link portfolio item to post
            await link_post_to_portfolio(db, portfolio_item_id, post.id)
            await db.commit()

            _publish(task_id, "done", post_id=str(post.id))

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()
            _publish(task_id, "error", message=str(e))
