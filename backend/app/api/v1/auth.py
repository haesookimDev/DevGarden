from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import GoogleAuthRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_or_create_user,
    verify_google_token,
)

router = APIRouter()


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with Google OAuth and return JWT tokens."""
    try:
        user_info = await verify_google_token(request.credential)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    user = await get_or_create_user(db, user_info)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    import uuid

    user_id = uuid.UUID(payload["sub"])
    from app.services.auth_service import get_user_by_id

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserResponse.model_validate(current_user)
