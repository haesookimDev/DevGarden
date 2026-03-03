from collections.abc import AsyncIterator

import anthropic

from app.ai.base import AIMessage, AIProvider


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model_name

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> AIMessage:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return AIMessage(
            content=response.content[0].text,
            model=self.model,
            usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        )

    async def generate_stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
