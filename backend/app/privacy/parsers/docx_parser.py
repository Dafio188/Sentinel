import zipfile
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any
from backend.app.privacy.parsers.base import BaseParser, ParsedDocument

class DocxParser(BaseParser):
    def parse(self, file_path: str, content_bytes: Optional[bytes] = None) -> ParsedDocument:
        metadata_entities: List[Dict[str, Any]] = []
        paragraphs: List[str] = []
        warnings: List[str] = []

        try:
            with zipfile.ZipFile(file_path if file_path else io.BytesIO(content_bytes)) as z:
                # 1. Parse core properties for author/lastModifiedBy
                if "docProps/core.xml" in z.namelist():
                    core_xml = z.read("docProps/core.xml")
                    tree = ET.fromstring(core_xml)
                    for elem in tree.iter():
                        tag_name = elem.tag.split("}")[-1]
                        if tag_name in ("creator", "lastModifiedBy") and elem.text:
                            metadata_entities.append({
                                "entity_type": "METADATA_AUTHOR",
                                "category": "IDENTIFIER",
                                "value": elem.text,
                                "field": tag_name,
                            })

                # 2. Parse main document text
                if "word/document.xml" in z.namelist():
                    doc_xml = z.read("word/document.xml")
                    tree = ET.fromstring(doc_xml)
                    for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                        texts = [node.text for node in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
                        if texts:
                            paragraphs.append("".join(texts))

                # 3. Check for comments
                if "word/comments.xml" in z.namelist():
                    comm_xml = z.read("word/comments.xml")
                    tree = ET.fromstring(comm_xml)
                    for comm in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment"):
                        author = comm.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author")
                        if author:
                            metadata_entities.append({
                                "entity_type": "METADATA_COMMENT_AUTHOR",
                                "category": "IDENTIFIER",
                                "value": author,
                                "field": "comment_author",
                            })
        except Exception as e:
            warnings.append(f"DOCX extraction warning: {str(e)}")
            if not paragraphs:
                paragraphs = [""]

        full_text = "\n\n".join(paragraphs)
        return ParsedDocument(
            text=full_text,
            spans_map=[],
            metadata=metadata_entities,
            warnings=warnings,
        )
