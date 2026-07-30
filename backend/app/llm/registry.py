import socket
import urllib.parse
from typing import Any, Dict, List, Optional
from backend.app.core.security import get_provider_api_key
from backend.app.db.engine import get_db_connection

class ProviderLockedError(Exception):
    """Raised when attempting to modify a locked privacy class (e.g., DeepSeek)."""
    pass

class ProviderRegistry:
    def get_providers(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM llm_providers")
            rows = [dict(r) for r in cursor.fetchall()]
            for p in rows:
                p["endpoint_verified_local"] = self.verify_loopback(p["id"], p["endpoint"], p["privacy_class"])
            return rows
        finally:
            conn.close()

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM llm_providers WHERE id = ?", (provider_id,))
            row = cursor.fetchone()
            if not row:
                return None
            p = dict(row)
            p["endpoint_verified_local"] = self.verify_loopback(p["id"], p["endpoint"], p["privacy_class"])
            return p
        finally:
            conn.close()

    def update_provider_privacy_class(self, provider_id: str, new_privacy_class: str) -> Dict[str, Any]:
        provider = self.get_provider(provider_id)
        if not provider:
            raise KeyError(f"Provider {provider_id} not found")

        if provider.get("privacy_class_locked") == 1:
            raise ProviderLockedError(f"Privacy class for provider {provider_id} is locked and cannot be modified.")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE llm_providers SET privacy_class = ? WHERE id = ?",
                (new_privacy_class, provider_id),
            )
            conn.commit()
        finally:
            conn.close()

        return self.get_provider(provider_id)  # type: ignore

    def verify_loopback(self, provider_id: str, endpoint: str, privacy_class: str) -> int:
        if privacy_class != "LOCAL":
            return 0
        try:
            parsed = urllib.parse.urlparse(endpoint)
            hostname = parsed.hostname or "127.0.0.1"
            ip = socket.gethostbyname(hostname)
            if ip.startswith("127.") or ip == "::1":
                return 1
        except Exception:
            pass
        return 0
