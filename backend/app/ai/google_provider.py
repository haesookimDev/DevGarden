from collections.abc import AsyncIterator

from google import genai

from app.ai.base import AIMessage, AIProvider


class GoogleProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model_name

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> AIMessage:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
            ),
        )
        return AIMessage(
            content=response.text or "",
            model=self.model,
            usage={
                "input_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "output_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            },
        )

    async def generate_stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> AsyncIterator[str]:
        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
            ),
        ):
            if chunk.text:
                yield chunk.text
