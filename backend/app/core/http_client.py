import urllib.parse
from typing import Any, Dict, List, Optional, Set
import httpx

class EgressBlockedError(Exception):
    """Raised when an HTTP request targets a host not listed in the egress allowlist."""
    pass

class GuardedHttpClient:
    def __init__(self, allowed_hosts: Optional[Set[str]] = None, audit_callback: Optional[Any] = None):
        # Always allow localhost loopback
        self.allowed_hosts: Set[str] = {"127.0.0.1", "localhost", "::1"}
        if allowed_hosts:
            self.allowed_hosts.update(allowed_hosts)
        self.audit_callback = audit_callback

    def add_allowed_host(self, host: str) -> None:
        self.allowed_hosts.add(host.lower())

    def check_url(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname or ""
        if hostname.lower() not in self.allowed_hosts:
            if self.audit_callback:
                self.audit_callback(
                    component="HTTP_CLIENT",
                    action="EGRESS_BLOCKED",
                    detail={"target_url": url, "target_host": hostname}
                )
            raise EgressBlockedError(
                f"Egress violation: Host '{hostname}' is not in the egress allowlist {list(self.allowed_hosts)}"
            )
        return hostname

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        self.check_url(url)
        async with httpx.AsyncClient() as client:
            return await client.get(url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        self.check_url(url)
        async with httpx.AsyncClient() as client:
            return await client.post(url, **kwargs)
