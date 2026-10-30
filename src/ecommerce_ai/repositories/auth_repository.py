"""Database operations used by the authentication service."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.models.auth_session import AuthSession
from ecommerce_ai.models.user import User


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(func.trim(User.email)) == email.strip().lower())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, *, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def create_session(self, *, user_id: int, token_hash: str, expires_at: datetime) -> AuthSession:
        auth_session = AuthSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(auth_session)
        await self.session.flush()
        return auth_session

    async def get_active_session(self, *, token_hash: str, now: datetime) -> tuple[AuthSession, User] | None:
        statement = (
            select(AuthSession, User)
            .join(User, User.id == AuthSession.user_id)
            .where(
                AuthSession.token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > now,
            )
        )
        result = await self.session.execute(statement)
        return result.one_or_none()

    async def revoke_session(self, *, token_hash: str, now: datetime) -> bool:
        auth_session = await self.session.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
            )
        )
        if auth_session is None:
            return False
        auth_session.revoked_at = now
        await self.session.flush()
        return True
