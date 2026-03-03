from app.ai.openai_provider import OpenAIProvider


class PrivateProvider(OpenAIProvider):
    """Provider for private/custom models using OpenAI-compatible API."""

    def __init__(self, api_key: str, model_name: str, base_url: str):
        super().__init__(api_key=api_key, model_name=model_name, base_url=base_url)
