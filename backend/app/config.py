from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "DevLog API"
    debug: bool = False
    secret_key: str = "change-this-to-a-random-secret-key"

    # Database
    database_url: str = "postgresql+asyncpg://devlog:devlog_secret@postgres:5432/devlog"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_secure: bool = False

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours
    jwt_refresh_token_expire_days: int = 30

    # File upload
    max_upload_size_mb: int = 100
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    allowed_document_types: list[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]

    # Encryption key for API keys
    encryption_key: str = "change-this-to-a-32-byte-key-!!"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
