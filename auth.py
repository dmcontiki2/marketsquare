# auth.py — API key protection for write endpoints
# Key is checked on all POST, PUT, DELETE requests.
# GET endpoints remain public (browse, listings, intros).

from fastapi import Header, HTTPException
import os

# Single API key — MUST be set as an environment variable on the server.
# There is deliberately NO default: if MS_API_KEY is unset we refuse to start,
# rather than silently accepting a guessable public key (S1, audit 31 May 2026).
API_KEY = os.environ.get("MS_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "MS_API_KEY environment variable is not set. Refusing to start without an "
        "API key — set it in the server environment before launching the BEA."
    )

def require_api_key(x_api_key: str = Header(default=None)):
    """Dependency — inject into any endpoint that needs protection."""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include X-Api-Key header."
        )
    return x_api_key
