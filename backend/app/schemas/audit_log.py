"""AuditLog schemas"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class AuditChangedBy(BaseModel):
    """Minimal user info for the person who made the change"""
    id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    """Response schema for a single audit log entry"""
    id: UUID
    tenant_id: UUID
    table_name: str
    record_id: UUID
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by_id: UUID
    changed_by: Optional[AuditChangedBy] = None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Response for listing audit log entries"""
    total: int
    audit_logs: List[AuditLogResponse]
