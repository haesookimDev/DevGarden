import re
import uuid
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider
from app.ai.prompts import document_to_blog, git_to_blog, portfolio_to_blog
from app.models.post import Post
from app.parsers.base import ParsedDocument


def _parse_ai_response(response: str) -> dict:
    """Parse structured AI response into blog post fields."""
    result = {"title": "", "excerpt": "", "content": "", "tags": [], "category": "tech"}

    # Extract title
    title_match = re.search(r"## Title\s*\n(.+)", response)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract excerpt
    excerpt_match = re.search(r"## Excerpt\s*\n(.+?)(?=\n## )", response, re.DOTALL)
    if excerpt_match:
        result["excerpt"] = excerpt_match.group(1).strip()

    # Extract content
    content_match = re.search(r"## Content\s*\n(.+?)(?=\n## Tags|\n## Category|$)", response, re.DOTALL)
    if content_match:
        result["content"] = content_match.group(1).strip()

    # Extract tags
    tags_match = re.search(r"## Tags\s*\n(.+)", response)
    if tags_match:
        result["tags"] = [t.strip() for t in tags_match.group(1).split(",")]

    # Extract category
    category_match = re.search(r"## Category\s*\n(.+)", response)
    if category_match:
        result["category"] = category_match.group(1).strip()

    return result


async def generate_from_document(
    provider: AIProvider,
    parsed_doc: ParsedDocument,
    filename: str,
    language: str = "ko",
) -> AsyncIterator[str]:
    """Generate blog post from parsed document content via streaming."""
    lang_name = "Korean" if language == "ko" else "English"
    user_prompt = document_to_blog.USER_PROMPT_TEMPLATE.format(
        filename=filename,
        content=parsed_doc.text[:100_000],  # Limit content size
        language=lang_name,
    )
    async for chunk in provider.generate_stream(
        system_prompt=document_to_blog.SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=8192,
    ):
        yield chunk


async def generate_from_git(
    provider: AIProvider,
    repo_analysis: dict,
    language: str = "ko",
) -> AsyncIterator[str]:
    """Generate blog post from Git repository analysis via streaming."""
    lang_name = "Korean" if language == "ko" else "English"
    user_prompt = git_to_blog.USER_PROMPT_TEMPLATE.format(
        **repo_analysis,
        language=lang_name,
    )
    async for chunk in provider.generate_stream(
        system_prompt=git_to_blog.SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=8192,
    ):
        yield chunk


async def generate_from_portfolio(
    provider: AIProvider,
    portfolio_data: dict,
    language: str = "ko",
) -> AsyncIterator[str]:
    """Generate blog post from portfolio item via streaming."""
    lang_name = "Korean" if language == "ko" else "English"
    user_prompt = portfolio_to_blog.USER_PROMPT_TEMPLATE.format(
        **portfolio_data,
        language=lang_name,
    )
    async for chunk in provider.generate_stream(
        system_prompt=portfolio_to_blog.SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=8192,
    ):
        yield chunk


async def save_generated_post(
    db: AsyncSession,
    user_id: uuid.UUID,
    ai_response: str,
    source_type: str,
    source_file_url: str | None = None,
) -> Post:
    """Parse AI response and save as draft post."""
    from app.services.post_service import _estimate_reading_time, _generate_slug

    parsed = _parse_ai_response(ai_response)

    post = Post(
        user_id=user_id,
        title=parsed["title"] or "Untitled Post",
        slug=_generate_slug(parsed["title"] or "untitled"),
        content=parsed["content"],
        excerpt=parsed["excerpt"],
        category=parsed["category"],
        tags=parsed["tags"],
        status="draft",
        source_type=source_type,
        source_file_url=source_file_url,
        reading_time_min=_estimate_reading_time(parsed["content"]),
    )
    db.add(post)
    await db.flush()
    return post
