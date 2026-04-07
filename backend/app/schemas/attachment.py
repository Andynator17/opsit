"""Attachment schemas"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class UploadedByInfo(BaseModel):
    """Minimal user info for the uploader"""
    id: UUID
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    """Response schema for a single attachment"""
    id: UUID
    task_id: UUID
    file_name: str
    file_size: int
    content_type: str
    uploaded_by_id: UUID
    uploaded_by: Optional[UploadedByInfo] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentListResponse(BaseModel):
    """Response for listing all attachments on a task"""
    total: int
    attachments: List[AttachmentResponse]
