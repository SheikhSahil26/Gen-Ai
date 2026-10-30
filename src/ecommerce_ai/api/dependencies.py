from collections.abc import AsyncIterator

from fastapi import Cookie, Depends, Header, HTTPException, status
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.auth.sessions import SESSION_COOKIE, hash_session_token, utc_now
from ecommerce_ai.db.database import AsyncSessionLocal
from ecommerce_ai.models.user import User
from ecommerce_ai.repositories.auth_repository import AuthRepository

ALLOWED_FRONTEND_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def require_request_origin(origin: str | None = Header(default=None)) -> None:
    if origin not in ALLOWED_FRONTEND_ORIGINS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )


async def get_current_user(
    raw_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    result = await AuthRepository(session).get_active_session(
        token_hash=hash_session_token(raw_token),
        now=utc_now(),
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or expired.",
        )
    _auth_session, user = result
    return user

# Shared checkpoint storage preserves conversations across request-scoped graph
# instances for the lifetime of this API process.
conversation_checkpointer = InMemorySaver()


async def get_main_graph() -> AsyncIterator[CompiledStateGraph]:
    # Import after settings have loaded so provider and LangSmith configuration
    # is established before agent models are constructed.
    from ecommerce_ai.graph.graph import build_graph

    async with AsyncSessionLocal() as session:
        yield build_graph(
            checkpointer=conversation_checkpointer,
            session=session,
        )
