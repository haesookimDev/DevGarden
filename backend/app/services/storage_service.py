import io
import uuid
from datetime import datetime

from minio import Minio
from minio.error import S3Error

from app.config import settings

BUCKET_IMAGES = "devlog-images"
BUCKET_DOCUMENTS = "devlog-documents"
BUCKET_AVATARS = "devlog-avatars"


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def ensure_buckets(self):
        """Create required buckets if they don't exist."""
        for bucket in [BUCKET_IMAGES, BUCKET_DOCUMENTS, BUCKET_AVATARS]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

    def upload_file(
        self,
        bucket: str,
        file_data: bytes,
        content_type: str,
        user_id: str,
        original_filename: str,
    ) -> str:
        """Upload file to MinIO and return the object path."""
        ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "bin"
        now = datetime.utcnow()
        object_name = f"{user_id}/{now.year}/{now.month:02d}/{uuid.uuid4()}.{ext}"

        self.client.put_object(
            bucket,
            object_name,
            io.BytesIO(file_data),
            length=len(file_data),
            content_type=content_type,
        )
        return f"{bucket}/{object_name}"

    def get_file(self, bucket: str, object_name: str) -> bytes:
        """Download file from MinIO."""
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def get_presigned_url(self, bucket: str, object_name: str, expires_hours: int = 24) -> str:
        """Generate a presigned URL for file access."""
        from datetime import timedelta

        return self.client.presigned_get_object(bucket, object_name, expires=timedelta(hours=expires_hours))

    def delete_file(self, bucket: str, object_name: str):
        """Delete a file from MinIO."""
        self.client.remove_object(bucket, object_name)
