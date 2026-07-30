from backend.app.privacy.parsers.base import ParserRegistry, ParsedDocument
from backend.app.privacy.parsers.txt_parser import TextParser
from backend.app.privacy.parsers.docx_parser import DocxParser
from backend.app.privacy.parsers.pdf_parser import PdfParser
from backend.app.privacy.parsers.image_parser import ImageParser

ParserRegistry.register("text/plain", TextParser())
ParserRegistry.register("text/csv", TextParser())
ParserRegistry.register("application/vnd.openxmlformats-officedocument.wordprocessingml.document", DocxParser())
ParserRegistry.register("application/pdf", PdfParser())
ParserRegistry.register("image/jpeg", ImageParser())
ParserRegistry.register("image/png", ImageParser())
