import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: str
    name: str
    bio: str | None = None
    github_url: str | None = None


class UserCreate(UserBase):
    google_id: str
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    github_url: str | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    avatar_url: str | None
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class GoogleAuthRequest(BaseModel):
    credential: str  # Google ID token
