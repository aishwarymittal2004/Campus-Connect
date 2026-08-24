import time
import uuid

from jose import JWTError

from app.core.config import settings
from app.core.exceptions import AlreadyExistsError, InvalidCredentialsError, NotFoundError, TokenError
from app.core.redis_client import RedisCache
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordChange, TokenPair, UserSignup


class AuthService:
    def __init__(self, user_repo: UserRepository, cache: RedisCache):
        self.user_repo = user_repo
        self.cache = cache

    async def signup(self, payload: UserSignup) -> User:
        if await self.user_repo.email_exists(payload.email):
            raise AlreadyExistsError("An account with this email already exists.")
        user = await self.user_repo.create(
            name=payload.name,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            phone=payload.phone,
            role=UserRole.STUDENT,
        )
        return user

    async def login(self, email: str, password: str) -> tuple[User, TokenPair]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Incorrect email or password.")
        if not user.is_active:
            raise InvalidCredentialsError("This account has been deactivated. Contact support.")
        tokens = self._issue_tokens(user)
        return user, tokens

    def _issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise TokenError("Invalid or expired refresh token.")

        if payload.token_type != TokenType.REFRESH.value:
            raise TokenError("Provided token is not a refresh token.")

        if await self.cache.is_blacklisted(payload.jti):
            raise TokenError("This refresh token has been revoked.")

        user = await self.user_repo.get_by_id(uuid.UUID(payload.sub))
        if not user or not user.is_active:
            raise TokenError("User no longer exists or is inactive.")

        # Rotate: blacklist the old refresh token's jti so it can't be reused
        ttl = max(payload.exp - int(time.time()), 1)
        await self.cache.add_to_blacklist(payload.jti, ttl_seconds=ttl)

        return self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            return  # already invalid - nothing to do
        ttl = max(payload.exp - int(time.time()), 1)
        await self.cache.add_to_blacklist(payload.jti, ttl_seconds=ttl)

    async def get_profile(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    async def update_profile(self, user_id: uuid.UUID, **fields) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return await self.user_repo.update(user, **fields)

    async def change_password(self, user_id: uuid.UUID, payload: PasswordChange) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        if not verify_password(payload.current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect.")
        await self.user_repo.update(user, password_hash=hash_password(payload.new_password))
