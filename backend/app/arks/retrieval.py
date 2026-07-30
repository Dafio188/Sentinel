from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.app.db.engine import get_db_connection

class ArksRetrieval:
    def search(
        self,
        query: str,
        kb_version: str = "KB-2026.07-B",
        eval_date: Optional[str] = None,
        top_k: int = 6,
    ) -> List[Dict[str, Any]]:
        eval_dt = eval_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query_words = [w.strip() for w in query.split() if len(w.strip()) > 3]

            cursor.execute(
                """
                SELECT c.*, s.title as source_title, s.legal_weight, s.authority
                FROM regulatory_chunks c
                JOIN regulatory_sources s ON c.source_id = s.id
                WHERE c.kb_version = ?
                  AND (c.effective_from IS NULL OR c.effective_from <= ?)
                  AND (c.effective_to IS NULL OR c.effective_to >= ?)
                """,
                (kb_version, eval_dt, eval_dt),
            )
            rows = [dict(r) for r in cursor.fetchall()]

            # Keyword RRF scoring fallback
            scored = []
            for r in rows:
                text_lower = r["text"].lower()
                score = sum(1 for w in query_words if w.lower() in text_lower)
                if score > 0 or len(query_words) == 0:
                    r["rrf_score"] = score
                    scored.append(r)

            scored.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
            return scored[:top_k]
        finally:
            conn.close()
