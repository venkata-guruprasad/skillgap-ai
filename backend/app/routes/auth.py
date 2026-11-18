"""Authentication API routes (register, login, current user)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    UserProfileResponse,
)
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    normalized_email = payload.email.strip().lower()
    if "@" not in normalized_email or "." not in normalized_email.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Please provide a valid email address.",
        )

    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=normalized_email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        role="student",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id), email=user.email)
    return AuthTokenResponse(
        access_token=token,
        user=UserProfileResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Authenticate and obtain a JWT access token",
)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    normalized_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    token = create_access_token(subject=str(user.id), email=user.email)
    return AuthTokenResponse(
        access_token=token,
        user=UserProfileResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get the currently authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update the currently authenticated user's profile",
)
def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    current_user.full_name = payload.full_name.strip()
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserProfileResponse.model_validate(current_user)
