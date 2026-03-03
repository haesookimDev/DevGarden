from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.config import settings
from app.models.user import User
from app.services.storage_service import BUCKET_DOCUMENTS, BUCKET_IMAGES, StorageService

router = APIRouter()


@router.post("/image")
async def upload_image(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    """Upload an image to MinIO."""
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed: {settings.allowed_image_types}",
        )

    contents = await file.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    storage = StorageService()
    path = storage.upload_file(
        BUCKET_IMAGES, contents, file.content_type, str(current_user.id), file.filename or "image"
    )
    url = storage.get_presigned_url(BUCKET_IMAGES, path.replace(f"{BUCKET_IMAGES}/", ""))

    return {"path": path, "url": url}


@router.post("/document")
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    """Upload a document (PDF, DOCX, PPTX) to MinIO."""
    if file.content_type not in settings.allowed_document_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Allowed: PDF, DOCX, PPTX",
        )

    contents = await file.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    storage = StorageService()
    path = storage.upload_file(
        BUCKET_DOCUMENTS, contents, file.content_type, str(current_user.id), file.filename or "document"
    )
    url = storage.get_presigned_url(BUCKET_DOCUMENTS, path.replace(f"{BUCKET_DOCUMENTS}/", ""))

    return {"path": path, "url": url, "filename": file.filename, "content_type": file.content_type}
