from typing import Optional
from backend.app.privacy.parsers.base import BaseParser, ParsedDocument

class ImageParser(BaseParser):
    def parse(self, file_path: str, content_bytes: Optional[bytes] = None) -> ParsedDocument:
        metadata = []
        # Extract basic EXIF GPS info if image file
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if b"GPS" in data or b"EXIF" in data:
                metadata.append({"entity_type": "METADATA_GPS", "category": "INDIRECT", "value": "EXIF_GPS_COORDINATES"})
        except Exception:
            pass

        return ParsedDocument(text="[IMAGE_CONTENT]", metadata=metadata)
