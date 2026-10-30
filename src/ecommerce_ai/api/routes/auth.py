"""Registration and cookie-backed session endpoints."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.api.dependencies import get_current_user, get_db_session, require_request_origin
from ecommerce_ai.config.settings import settings
from ecommerce_ai.models.user import User
from ecommerce_ai.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from ecommerce_ai.auth.sessions import SESSION_COOKIE, SESSION_TTL
from ecommerce_ai.services.auth import AuthService, IdentityAlreadyRegistered, InvalidCredentials


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_session_cookie(response: Response, *, token: str, max_age: int) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    _origin: None = Depends(require_request_origin),
) -> AuthResponse:
    service = AuthService(session)
    try:
        user = await service.register(
            username=request.username,
            email=request.email,
            password=request.password,
        )
    except IdentityAlreadyRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email or username already exists.",
        ) from exc

    issued = await service.issue_session(user)
    _set_session_cookie(response, token=issued.raw_token, max_age=int(SESSION_TTL.total_seconds()))
    return AuthResponse(user=UserResponse.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    _origin: None = Depends(require_request_origin),
) -> AuthResponse:
    service = AuthService(session)
    try:
        user = await service.authenticate(email=request.email, password=request.password)
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Cookie"},
        ) from exc

    issued = await service.issue_session(user)
    _set_session_cookie(response, token=issued.raw_token, max_age=int(SESSION_TTL.total_seconds()))
    return AuthResponse(user=UserResponse.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    raw_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    _origin: None = Depends(require_request_origin),
) -> Response:
    if raw_token:
        await AuthService(session).revoke_session(raw_token)
    _clear_session_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)
