"""Attachment API endpoints - File upload, download, list, delete for tasks/tickets"""
import os
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentResponse, AttachmentListResponse

router = APIRouter(prefix="/tasks/{task_id}/attachments", tags=["attachments"])

ALLOWED_CONTENT_TYPES = {
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv",
    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "image/bmp",
    # Archives
    "application/zip",
    "application/x-7z-compressed",
    "application/gzip",
    "application/x-rar-compressed",
    # Data
    "text/xml",
    "application/json",
    "application/xml",
    # Email
    "message/rfc822",
    # Fallback for unknown types (browsers sometimes send this)
    "application/octet-stream",
}


def _get_upload_dir(tenant_id: uuid.UUID) -> str:
    """Get tenant-specific upload directory, creating it if needed."""
    path = os.path.join(settings.UPLOAD_DIR, str(tenant_id))
    os.makedirs(path, exist_ok=True)
    return path


async def _verify_task_access(
    task_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> Task:
    """Verify the task exists and belongs to the tenant."""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == tenant_id,
            Task.is_deleted == False,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("/", response_model=List[AttachmentResponse], status_code=status.HTTP_201_CREATED)
async def upload_attachments(
    task_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload one or more files to a task."""
    await _verify_task_access(task_id, current_user.tenant_id, db)

    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_FILES_PER_UPLOAD} files per upload",
        )

    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    upload_dir = _get_upload_dir(current_user.tenant_id)
    created_attachments = []

    for upload_file in files:
        # Validate content type
        if upload_file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{upload_file.content_type}' is not allowed for '{upload_file.filename}'",
            )

        # Read file and check size
        content = await upload_file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{upload_file.filename}' exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB",
            )

        # Generate collision-free stored filename
        file_ext = os.path.splitext(upload_file.filename or "file")[1]
        stored_name = f"{uuid.uuid4()}{file_ext}"

        # Write file to disk
        file_path = os.path.join(upload_dir, stored_name)
        with open(file_path, "wb") as f:
            f.write(content)

        # Create database record
        attachment = Attachment(
            tenant_id=current_user.tenant_id,
            task_id=task_id,
            file_name=upload_file.filename or "unnamed",
            stored_file_name=stored_name,
            file_size=len(content),
            content_type=upload_file.content_type or "application/octet-stream",
            uploaded_by_id=current_user.id,
        )
        db.add(attachment)
        created_attachments.append(attachment)

    await db.commit()
    for att in created_attachments:
        await db.refresh(att)

    return created_attachments


@router.get("/", response_model=AttachmentListResponse)
async def list_attachments(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all attachments for a task."""
    await _verify_task_access(task_id, current_user.tenant_id, db)

    result = await db.execute(
        select(Attachment).where(
            Attachment.task_id == task_id,
            Attachment.tenant_id == current_user.tenant_id,
            Attachment.is_deleted == False,
        ).order_by(Attachment.created_at.desc())
    )
    attachments = result.scalars().all()

    return AttachmentListResponse(
        total=len(attachments),
        attachments=attachments,
    )


@router.get("/{attachment_id}/download")
async def download_attachment(
    task_id: uuid.UUID,
    attachment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a specific attachment file."""
    await _verify_task_access(task_id, current_user.tenant_id, db)

    result = await db.execute(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.task_id == task_id,
            Attachment.tenant_id == current_user.tenant_id,
            Attachment.is_deleted == False,
        )
    )
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    file_path = os.path.join(
        settings.UPLOAD_DIR,
        str(current_user.tenant_id),
        attachment.stored_file_name,
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    return FileResponse(
        path=file_path,
        filename=attachment.file_name,
        media_type=attachment.content_type,
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    task_id: uuid.UUID,
    attachment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an attachment."""
    await _verify_task_access(task_id, current_user.tenant_id, db)

    result = await db.execute(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.task_id == task_id,
            Attachment.tenant_id == current_user.tenant_id,
            Attachment.is_deleted == False,
        )
    )
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    attachment.is_deleted = True
    attachment.deleted_at = datetime.now(timezone.utc)

    await db.commit()
    return None
