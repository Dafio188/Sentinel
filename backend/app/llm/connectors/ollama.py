from typing import Any, Dict, Optional
from backend.app.core.http_client import GuardedHttpClient
from backend.app.llm.connectors.base import BaseLLMConnector

class OllamaConnector(BaseLLMConnector):
    def __init__(self, endpoint: str = "http://127.0.0.1:11434", model: str = "gemma3:4b", num_ctx: int = 16384):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.num_ctx = num_ctx
        self.http_client = GuardedHttpClient()

    async def generate_chat(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.endpoint}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"num_ctx": self.num_ctx},
        }

        try:
            resp = await self.http_client.post(url, json=payload, timeout=120.0)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                return {"text": content, "status": "SUCCESS", "raw": data}
            return {"text": f"[Errore HTTP Ollama: {resp.status_code}]", "status": "ERROR"}
        except Exception as e:
            return {"text": f"[Impossibile connettersi ad Ollama ({self.endpoint}): {str(e)}. Assicurati che Ollama sia in esecuzione.]", "status": "ERROR"}
