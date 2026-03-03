import uuid
from datetime import datetime

from pydantic import BaseModel


class AIConfigBase(BaseModel):
    provider: str  # 'claude', 'openai', 'google', 'private'
    model_name: str | None = None
    base_url: str | None = None  # For private models
    is_default: bool = False


class AIConfigCreate(AIConfigBase):
    api_key: str  # Plain text, will be encrypted


class AIConfigUpdate(BaseModel):
    model_name: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class AIConfigResponse(AIConfigBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    # NOTE: api_key is never returned

    model_config = {"from_attributes": True}


class GenerateFromDocumentRequest(BaseModel):
    file_url: str  # MinIO URL of uploaded document
    language: str = "ko"  # 'ko' or 'en'


class GenerateFromGitRequest(BaseModel):
    repo_url: str  # GitHub/GitLab URL
    access_token: str | None = None  # For private repos
    language: str = "ko"


class GenerateFromPortfolioRequest(BaseModel):
    portfolio_item_id: uuid.UUID
    language: str = "ko"


class GenerationTaskResponse(BaseModel):
    id: uuid.UUID
    task_type: str
    status: str
    error_message: str | None
    result_post_id: uuid.UUID | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
