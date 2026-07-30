import secrets
from typing import Dict, Optional
try:
    import keyring
except ImportError:
    keyring = None
from fastapi import Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

# Global session token generated per server process run
SESSION_TOKEN = secrets.token_hex(32)

_IN_MEMORY_KEYSTORE: Dict[str, str] = {}

def get_session_token() -> str:
    return SESSION_TOKEN

def store_provider_api_key(provider_id: str, api_key: str) -> None:
    """Store provider API key securely in OS keyring (never to disk or DB)."""
    service_name = f"aigate/{provider_id}"
    if keyring is not None:
        try:
            keyring.set_password(service_name, "api_key", api_key)
            return
        except Exception:
            pass
    # Fallback to in-memory non-persisted store if keyring is unavailable (e.g. headless CI)
    _IN_MEMORY_KEYSTORE[provider_id] = api_key

def get_provider_api_key(provider_id: str) -> Optional[str]:
    """Retrieve provider API key from OS keyring."""
    service_name = f"aigate/{provider_id}"
    if keyring is not None:
        try:
            val = keyring.get_password(service_name, "api_key")
            if val:
                return val
        except Exception:
            pass
    return _IN_MEMORY_KEYSTORE.get(provider_id)

async def verify_session_middleware(request: Request, call_next):
    """Enforce localhost session token on all endpoints except /health."""
    if request.url.path == "/health":
        return await call_next(request)
    
    token = request.headers.get("X-Session-Token")
    if not token or token != SESSION_TOKEN:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized: Invalid or missing X-Session-Token header"},
        )
    return await call_next(request)
