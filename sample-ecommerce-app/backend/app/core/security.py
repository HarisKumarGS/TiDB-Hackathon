from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwk, jwt
from jose.utils import base64url_decode
from typing import Any, Dict
import json
import httpx

from app.core.config import settings


bearer_scheme = HTTPBearer(auto_error=False)


_JWKS_CACHE: Dict[str, Any] | None = None


async def get_jwks() -> Dict[str, Any]:
    global _JWKS_CACHE
    if _JWKS_CACHE:
        return _JWKS_CACHE
    jwks_url = settings.cognito_jwks_url or (
        f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
        f"/{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(jwks_url)
        resp.raise_for_status()
        _JWKS_CACHE = resp.json()
        return _JWKS_CACHE


async def verify_cognito_jwt(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    alg = headers.get("alg")

    jwks = await get_jwks()
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    public_key = jwk.construct(key)
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

    if not public_key.verify(message.encode('utf-8'), decoded_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    claims = jwt.get_unverified_claims(token)
    if claims.get("token_use") != "id" and claims.get("token_use") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token use")

    if settings.cognito_app_client_id and claims.get("aud") not in [settings.cognito_app_client_id, claims.get("client_id")]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")

    return claims

