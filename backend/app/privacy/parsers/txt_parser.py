import os
from typing import Optional
from backend.app.privacy.parsers.base import BaseParser, ParsedDocument

class TextParser(BaseParser):
    def parse(self, file_path: str, content_bytes: Optional[bytes] = None) -> ParsedDocument:
        if content_bytes is None:
            with open(file_path, "rb") as f:
                content_bytes = f.read()

        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = content_bytes.decode("latin-1", errors="replace")

        return ParsedDocument(
            text=text,
            spans_map=[],
            metadata=[],
            warnings=[],
        )
