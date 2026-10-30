"""Account registration, login, and revocable session operations."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.auth.passwords import hash_password, verify_password
from ecommerce_ai.auth.sessions import (
    SESSION_TTL,
    hash_session_token,
    new_session_token,
    utc_now,
)
from ecommerce_ai.models.auth_session import AuthSession
from ecommerce_ai.models.user import User
from ecommerce_ai.repositories.auth_repository import AuthRepository


class IdentityAlreadyRegistered(Exception):
    """Email or username conflicts with an existing account."""


class InvalidCredentials(Exception):
    """The supplied login credentials are invalid."""


@dataclass(frozen=True)
class IssuedSession:
    user: User
    raw_token: str
    expires_at: datetime


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AuthRepository(session)

    async def register(self, *, username: str, email: str, password: str) -> User:
        try:
            user = await self.repository.create_user(
                username=username,
                email=email.strip().lower(),
                hashed_password=hash_password(password),
            )
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as error:
            await self.session.rollback()
            raise IdentityAlreadyRegistered from error

    async def authenticate(self, *, email: str, password: str) -> User:
        user = await self.repository.get_user_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentials
        return user

    async def issue_session(self, user: User) -> IssuedSession:
        raw_token = new_session_token()
        expires_at = utc_now() + SESSION_TTL
        await self.repository.create_session(
            user_id=user.id,
            token_hash=hash_session_token(raw_token),
            expires_at=expires_at,
        )
        await self.session.commit()
        return IssuedSession(user=user, raw_token=raw_token, expires_at=expires_at)

    async def resolve_session(self, raw_token: str) -> tuple[AuthSession, User] | None:
        return await self.repository.get_active_session(
            token_hash=hash_session_token(raw_token),
            now=utc_now(),
        )

    async def revoke_session(self, raw_token: str) -> bool:
        revoked = await self.repository.revoke_session(
            token_hash=hash_session_token(raw_token),
            now=utc_now(),
        )
        await self.session.commit()
        return revoked
