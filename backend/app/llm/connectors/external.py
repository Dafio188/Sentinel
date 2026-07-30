from typing import Any, Dict, Optional
from backend.app.core.http_client import EgressBlockedError, GuardedHttpClient
from backend.app.core.security import get_provider_api_key
from backend.app.llm.connectors.base import BaseLLMConnector

class ExternalLLMConnector(BaseLLMConnector):
    def __init__(self, provider_id: str, endpoint: str, model: str, allowed_hosts: Optional[set] = None):
        self.provider_id = provider_id
        self.endpoint = endpoint
        self.model = model
        self.http_client = GuardedHttpClient(allowed_hosts=allowed_hosts or {self._extract_host(endpoint)})

    def _extract_host(self, url: str) -> str:
        import urllib.parse
        return urllib.parse.urlparse(url).hostname or url

    async def generate_chat(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        api_key = get_provider_api_key(self.provider_id)
        # Check egress allowlist via http_client
        self.http_client.check_url(self.endpoint)

        return {
            "text": f"[{self.provider_id.upper()} external response for: {prompt[:40]}]",
            "status": "SUCCESS",
            "provider_id": self.provider_id,
        }
