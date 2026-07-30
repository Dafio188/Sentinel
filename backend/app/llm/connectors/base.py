from typing import Any, Dict, Optional

class BaseLLMConnector:
    async def generate_chat(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement generate_chat()")
