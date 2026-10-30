"""Opaque session credential helpers. Only a digest is persisted in the DB."""

from datetime import datetime, timedelta, timezone
import hashlib
import secrets


SESSION_TTL = timedelta(days=7)
SESSION_COOKIE = "cg_session"


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
