"""
Security primitives: password hashing and JWT access/refresh token handling.
Kept separate from business logic so it can be unit tested in isolation.
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta, extra_claims: Optional[dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        subject=user_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"role": role},
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        subject=user_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


class TokenPayload:
    def __init__(self, sub: str, role: Optional[str], token_type: str, jti: str, exp: int):
        self.sub = sub
        self.role = role
        self.token_type = token_type
        self.jti = jti
        self.exp = exp


def decode_token(token: str) -> TokenPayload:
    """Raises jose.JWTError if invalid/expired - caller is responsible for translating to HTTP errors."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return TokenPayload(
        sub=payload["sub"],
        role=payload.get("role"),
        token_type=payload["type"],
        jti=payload["jti"],
        exp=payload["exp"],
    )


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "TokenType",
    "TokenPayload",
    "JWTError",
]
