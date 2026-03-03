from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class AIMessage:
    content: str
    model: str
    usage: dict | None = None


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> AIMessage:
        """Generate a complete response."""
        ...

    @abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Generate a streaming response, yielding text chunks."""
        ...
