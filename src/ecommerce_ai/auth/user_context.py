"""Request-scoped authenticated identity for agent tool calls."""

from contextlib import contextmanager
from contextvars import ContextVar, Token
from collections.abc import Iterator


_current_user_id: ContextVar[int | None] = ContextVar("current_user_id", default=None)


def get_user_id() -> int:
    user_id = _current_user_id.get()
    if user_id is None:
        raise RuntimeError("No authenticated user is active for this request.")
    return user_id


@contextmanager
def authenticated_user(user_id: int) -> Iterator[None]:
    token: Token[int | None] = _current_user_id.set(user_id)
    try:
        yield
    finally:
        _current_user_id.reset(token)
