from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.ai.base import AIMessage, AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o", base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model_name

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> AIMessage:
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = response.choices[0]
        return AIMessage(
            content=choice.message.content or "",
            model=self.model,
            usage={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        )

    async def generate_stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
