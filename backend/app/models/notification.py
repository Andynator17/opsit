"""Notification model - User notifications (table only, no logic yet)"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Notification(Base, BaseModelMixin):
    """Notifications for users (assignments, status changes, SLA breaches, etc.)"""

    __tablename__ = "notifications"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # recipient

    type = Column(String(50), nullable=False)  # "assignment", "status_change", "sla_breach", "comment"
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)

    related_record_id = Column(UUID(as_uuid=True), nullable=True)
    related_record_type = Column(String(50), nullable=True)  # "task", "incident", etc.

    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("idx_notifications_tenant_user", "tenant_id", "user_id"),
        Index("idx_notifications_user_unread", "user_id", "is_read"),
    )

    def __repr__(self):
        return f"<Notification {self.type}: {self.title}>"
