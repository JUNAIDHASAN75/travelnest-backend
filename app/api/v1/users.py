from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile"
)
def update_current_user_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if request.name is not None:
        current_user.name = request.name.strip()
    if request.email is not None and request.email.lower() != current_user.email:
        existing = db.query(User).filter(User.email == request.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already in use by another account"
            )
        current_user.email = request.email.lower().strip()

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users (Admin only)"
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(User).order_by(User.id.asc()).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=UserResponse,
    summary="Get user details by ID (Admin only)"
)
def get_user_by_id(
    id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found"
        )
    return user


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate/remove user (Admin only)"
)
def delete_user(
    id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found"
        )
    db.delete(user)
    db.commit()
