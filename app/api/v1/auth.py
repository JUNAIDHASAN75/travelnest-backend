from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    MessageResponse
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email, name, and strong password.
    Passwords are encrypted with Argon2id.
    """
    user = AuthService.register_user(db, request)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and obtain JWT tokens"
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with email and password to receive access and refresh tokens.
    """
    user = AuthService.authenticate_user(db, request.email, request.password)
    return AuthService.create_tokens_for_user(db, user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a valid refresh token"
)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Exchange an existing valid refresh token for a fresh access token and a new rotated refresh token.
    """
    return AuthService.refresh_token(db, request.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out by revoking refresh token"
)
def logout(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Revoke a refresh token so it cannot be used again.
    """
    AuthService.revoke_token(db, request.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile"
)
def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Return profile data of the currently logged-in user.
    """
    return current_user
