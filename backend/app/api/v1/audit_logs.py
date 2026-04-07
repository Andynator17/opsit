"""AuditLog API endpoints - View audit trail for tasks"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogListResponse

router = APIRouter(prefix="/tasks/{task_id}/audit-logs", tags=["audit-logs"])


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all audit log entries for a task, ordered newest first."""
    # Verify task exists and belongs to tenant
    task_result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False,
        )
    )
    if not task_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    result = await db.execute(
        select(AuditLog)
        .options(selectinload(AuditLog.changed_by))
        .where(
            AuditLog.record_id == task_id,
            AuditLog.tenant_id == current_user.tenant_id,
            AuditLog.table_name == "tasks",
        ).order_by(AuditLog.changed_at.desc())
    )
    logs = result.scalars().all()

    return AuditLogListResponse(
        total=len(logs),
        audit_logs=logs,
    )
