from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token
)
from app.models.user import User, RefreshToken, UserRole
from app.schemas.auth import RegisterRequest, TokenResponse


class AuthService:
    @staticmethod
    def register_user(db: Session, req: RegisterRequest) -> User:
        existing_user = db.query(User).filter(User.email == req.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists"
            )

        hashed = hash_password(req.password)
        new_user = User(
            name=req.name.strip(),
            email=req.email.lower().strip(),
            password_hash=hashed,
            role=UserRole.USER,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact support."
            )
        return user

    @staticmethod
    def create_tokens_for_user(db: Session, user: User) -> TokenResponse:
        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role.value)

        token_hash = hash_token(refresh_token)
        decoded = decode_token(refresh_token)
        exp_ts = decoded.get("exp") if decoded else None
        expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc) if exp_ts else datetime.now(timezone.utc)

        db_refresh = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            revoked=False,
            expires_at=expires_at
        )
        db.add(db_refresh)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    def refresh_token(db: Session, raw_refresh_token: str) -> TokenResponse:
        payload = decode_token(raw_refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token_hash = hash_token(raw_refresh_token)
        db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

        if not db_token or db_token.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or is invalid",
                headers={"WWW-Authenticate": "Bearer"}
            )

        now = datetime.now(timezone.utc)
        token_expiry = db_token.expires_at
        if token_expiry.tzinfo is None:
            token_expiry = token_expiry.replace(tzinfo=timezone.utc)

        if token_expiry < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Token rotation: revoke old token
        db_token.revoked = True
        db.commit()

        # Issue new pair
        return AuthService.create_tokens_for_user(db, user)

    @staticmethod
    def revoke_token(db: Session, raw_refresh_token: str) -> None:
        token_hash = hash_token(raw_refresh_token)
        db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if db_token:
            db_token.revoked = True
            db.commit()
