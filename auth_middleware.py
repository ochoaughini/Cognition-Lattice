"""Simple JWT auth middleware for FastAPI."""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

bearer = HTTPBearer()


def verify_jwt(token: str) -> bool:
    secret = "secret"
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        return True
    except jwt.PyJWTError:
        return False


async def auth_dependency(request: Request) -> None:
    credentials: HTTPAuthorizationCredentials = await bearer(request)
    if not verify_jwt(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
