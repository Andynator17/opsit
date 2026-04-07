"""AuditLog model - Tracks field-level changes on records"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class AuditLog(Base):
    """Stores individual field-level audit entries for any record."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    # What was changed
    table_name = Column(String(100), nullable=False)  # "tasks", "users", etc.
    record_id = Column(UUID(as_uuid=True), nullable=False)  # ID of changed record
    action = Column(String(20), nullable=False)  # "create", "update", "delete"

    # Field-level detail (nullable for create/delete actions)
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    # Who and when
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    changed_by = relationship("User", foreign_keys=[changed_by_id], lazy="joined")

    __table_args__ = (
        Index("idx_audit_tenant_table_record", "tenant_id", "table_name", "record_id"),
        Index("idx_audit_tenant_changed_at", "tenant_id", "changed_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} {self.table_name}.{self.field_name}>"
