from enum import IntEnum
from functools import wraps
from typing import Any, Callable, TypeVar

class Zone(IntEnum):
    ZONE_0 = 0  # Vault, original documents, unmasked secrets (Strict Local)
    ZONE_1 = 1  # Processed/protected documents, pipeline DB, local embeddings
    ZONE_2 = 2  # External Egress (LLM external API calls)

class ZoneViolationError(Exception):
    """Raised when an operation violates physical zone isolation (Invariant I1)."""
    pass

class ZonedPayload:
    def __init__(self, data: Any, zone: Zone | int):
        self.data = data
        self.zone = Zone(zone)

    def __repr__(self) -> str:
        return f"<ZonedPayload zone={self.zone.name} ({self.zone.value})>"

F = TypeVar("F", bound=Callable[..., Any])

def requires_zone_max(max_zone: Zone | int) -> Callable[[F], F]:
    """
    Decorator enforcing that no argument passed to the function carries a Zone value higher
    or lower than allowed, and specifically blocking Zone 0 payloads from entering higher zones.
    """
    allowed_max = Zone(max_zone)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            all_args = list(args) + list(kwargs.values())
            for arg in all_args:
                if isinstance(arg, ZonedPayload):
                    if arg.zone < allowed_max: # e.g. passing Zone 0 to a function expecting Zone 1 or 2 max input
                        raise ZoneViolationError(
                            f"Zone violation: Payload from Zone {arg.zone.value} cannot be passed to a function restricted to max input Zone {allowed_max.value}"
                        )
                    if arg.zone > allowed_max:
                        raise ZoneViolationError(
                            f"Zone violation: Payload zone {arg.zone.value} exceeds maximum permitted zone {allowed_max.value}"
                        )
            return func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator
