import uuid
from datetime import datetime, timedelta, timezone

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate


async def verify_google_token(credential: str) -> dict:
    """Verify Google ID token and return user info."""
    idinfo = id_token.verify_oauth2_token(
        credential,
        google_requests.Request(),
        settings.google_client_id,
    )
    return {
        "google_id": idinfo["sub"],
        "email": idinfo["email"],
        "name": idinfo.get("name", ""),
        "avatar_url": idinfo.get("picture"),
    }


async def get_or_create_user(db: AsyncSession, user_info: dict) -> tuple[User, bool]:
    """Get existing user by Google ID or create new one. Returns (user, is_new)."""
    stmt = select(User).where(User.google_id == user_info["google_id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user, False

    user = User(
        email=user_info["email"],
        name=user_info["name"],
        google_id=user_info["google_id"],
        avatar_url=user_info.get("avatar_url"),
    )
    db.add(user)
    await db.flush()
    return user, True


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
