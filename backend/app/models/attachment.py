"""Attachment model - File attachments for tasks/tickets"""
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Attachment(Base, BaseModelMixin):
    """File metadata for any task/ticket type. Files stored on local filesystem."""

    __tablename__ = "attachments"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Link to task (works for all ticket types)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True)

    # File metadata
    file_name = Column(String(255), nullable=False)
    stored_file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)

    # Who uploaded
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id], lazy="joined")

    __table_args__ = (
        Index('idx_attachments_tenant_task', 'tenant_id', 'task_id'),
    )

    def __repr__(self):
        return f"<Attachment {self.file_name} ({self.file_size} bytes)>"
