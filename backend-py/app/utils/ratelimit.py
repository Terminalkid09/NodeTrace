from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_device_token(request: Request) -> str:
    """Extract device token from Authorization header for agent rate limiting."""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return get_remote_address(request)

def get_user_token(request: Request) -> str:
    """Use remote address for admin endpoints (could be enhanced with user ID)."""
    return get_remote_address(request)

# Main limiter for general use
limiter = Limiter(key_func=get_remote_address)

# Device-specific limiter for agent endpoints
device_limiter = Limiter(key_func=get_device_token)

# User-specific limiter for admin endpoints
user_limiter = Limiter(key_func=get_user_token)