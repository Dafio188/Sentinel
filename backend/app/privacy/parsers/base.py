from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ParsedDocument:
    text: str
    spans_map: List[Dict[str, Any]] = field(default_factory=list)
    metadata: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class BaseParser:
    def parse(self, file_path: str, content_bytes: Optional[bytes] = None) -> ParsedDocument:
        raise NotImplementedError("Subclasses must implement parse()")

class ParserRegistry:
    _parsers: Dict[str, BaseParser] = {}

    @classmethod
    def register(cls, mime_type: str, parser: BaseParser) -> None:
        cls._parsers[mime_type.lower()] = parser

    @classmethod
    def get_parser(cls, mime_type: str) -> Optional[BaseParser]:
        return cls._parsers.get(mime_type.lower())
