import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings
from backend.app.db.engine import get_db_connection

class ArksIngestor:
    def ingest_source_text(
        self,
        source_id: str,
        title: str,
        authority: str,
        legal_weight: str,
        text_content: str,
        kb_version: str = "KB-2026.07-B",
        language: str = "ita",
    ) -> int:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO regulatory_sources (id, title, authority, legal_weight, version_label, retrieved_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
                """,
                (source_id, title, authority, legal_weight, kb_version),
            )

            # EUR-Lex Structural Chunking: 1 chunk = 1 article/paragraph/recital
            paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]
            chunk_count = 0

            for i, p_text in enumerate(paragraphs):
                chunk_id = f"{source_id}_CHUNK_{i+1:04d}"
                art_match = re.search(r'(Articolo|Art\.|Considerando)\s*(\d+)', p_text, re.IGNORECASE)
                article = art_match.group(2) if art_match else None

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO regulatory_chunks (
                        id, source_id, article, paragraph, text, language, kb_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (chunk_id, source_id, article, str(i+1), p_text, language, kb_version),
                )
                chunk_count += 1

            conn.commit()
            return chunk_count
        finally:
            conn.close()
