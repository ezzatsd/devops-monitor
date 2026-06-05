import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader


API_KEY = os.getenv("API_KEY", "demo-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> str:
    """Validate the X-API-Key header for protected write endpoints."""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key",
        )
    return api_key
