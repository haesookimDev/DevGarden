from app.ai.base import AIProvider
from app.ai.claude_provider import ClaudeProvider
from app.ai.google_provider import GoogleProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.private_provider import PrivateProvider


class AIProviderFactory:
    """Factory to create AI provider instances."""

    @staticmethod
    def create(
        provider: str,
        api_key: str,
        model_name: str | None = None,
        base_url: str | None = None,
    ) -> AIProvider:
        match provider:
            case "claude":
                return ClaudeProvider(api_key=api_key, model_name=model_name or "claude-sonnet-4-20250514")
            case "openai":
                return OpenAIProvider(api_key=api_key, model_name=model_name or "gpt-4o")
            case "google":
                return GoogleProvider(api_key=api_key, model_name=model_name or "gemini-2.0-flash")
            case "private":
                if not base_url:
                    raise ValueError("base_url is required for private provider")
                return PrivateProvider(api_key=api_key, model_name=model_name or "default", base_url=base_url)
            case _:
                raise ValueError(f"Unknown provider: {provider}")
