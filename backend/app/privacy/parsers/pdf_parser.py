from typing import Optional
from backend.app.privacy.parsers.base import BaseParser, ParsedDocument

class PdfParser(BaseParser):
    def parse(self, file_path: str, content_bytes: Optional[bytes] = None) -> ParsedDocument:
        # Fallback pdf parser reading raw text if pdfplumber is absent
        text = ""
        metadata = []
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()
            text = raw_data.decode("latin-1", errors="ignore")
            # Extract basic PDF metadata keys if present
            if b"/Author" in raw_data:
                metadata.append({"entity_type": "METADATA_AUTHOR", "category": "IDENTIFIER", "value": "PDF_Author"})
        except Exception:
            text = ""

        return ParsedDocument(text=text, metadata=metadata)
