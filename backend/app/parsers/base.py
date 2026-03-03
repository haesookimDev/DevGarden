from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedDocument:
    text: str
    images: list[bytes] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    page_count: int = 0


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_data: bytes) -> ParsedDocument:
        """Parse document bytes and return structured content."""
        ...
