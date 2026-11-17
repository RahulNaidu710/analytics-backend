from typing import Optional

from fastapi import Depends, Header, HTTPException

from settings import platform_settings


async def validate_api_key(
    platform_api_key: Optional[str] = Header(None),
    settings=Depends(platform_settings),
):
    if not platform_api_key:
        raise HTTPException(status_code=401, detail="API KEY not provided")
    if platform_api_key != settings.platform_api_key:
        raise HTTPException(status_code=401, detail="Invalid API KEY")
