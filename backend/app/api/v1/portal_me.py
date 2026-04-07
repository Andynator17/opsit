"""Portal 'Me' endpoints — user-scoped for self-service portal"""
import uuid as uuid_mod
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rule_engine import execute_rules
from app.models.user import User
from app.models.task import Task
from app.models.support_group import SupportGroup
from app.models.category import Category
from app.models.audit_log import AuditLog
from app.schemas.task import TaskResponse, TaskListResponse
from app.schemas.portal import PortalMyStatsResponse

router = APIRouter(prefix="/portal/me", tags=["portal"])


# Priority calculation (same as tasks.py)
PRIORITY_MATRIX = {
    ("critical", "critical"): "critical",
    ("critical", "high"): "critical",
    ("high", "critical"): "critical",
    ("high", "high"): "high",
    ("critical", "medium"): "high",
    ("medium", "critical"): "high",
    ("critical", "low"): "high",
    ("low", "critical"): "high",
    ("high", "medium"): "high",
    ("medium", "high"): "high",
    ("high", "low"): "medium",
    ("low", "high"): "medium",
    ("medium", "medium"): "medium",
    ("medium", "low"): "low",
    ("low", "medium"): "low",
    ("low", "low"): "low",
}


def _portal_task_load_options():
    """Selectinload options for portal task responses."""
    return [
        selectinload(Task.opened_by),
        selectinload(Task.caller),
        selectinload(Task.affected_user),
        selectinload(Task.assigned_to),
        selectinload(Task.assignment_group),
        selectinload(Task.resolved_by),
        selectinload(Task.closed_by),
        selectinload(Task.company),
    ]


@router.get("/stats", response_model=PortalMyStatsResponse)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ticket stats for the current user"""
    base = select(Task.sys_class_name, Task.status, func.count(Task.id)).where(
        Task.tenant_id == current_user.tenant_id,
        Task.caller_id == current_user.id,
        Task.is_deleted == False,
    ).group_by(Task.sys_class_name, Task.status)

    result = await db.execute(base)
    rows = result.all()

    open_statuses = {"new", "assigned", "in_progress", "pending", "submitted", "pending_approval", "approved"}
    open_incidents = 0
    open_requests = 0
    pending_approvals = 0
    total = 0

    for sys_class, stat, count in rows:
        total += count
        if sys_class == "incident" and stat in open_statuses:
            open_incidents += count
        elif sys_class == "request" and stat in open_statuses:
            open_requests += count
        elif sys_class == "approval" and stat == "pending":
            pending_approvals += count

    # Resolved in last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    resolved_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == current_user.tenant_id,
            Task.caller_id == current_user.id,
            Task.is_deleted == False,
            Task.resolved_at >= thirty_days_ago,
        )
    )
    resolved_count = resolved_result.scalar() or 0

    return PortalMyStatsResponse(
        open_incidents=open_incidents,
        open_requests=open_requests,
        pending_approvals=pending_approvals,
        resolved_last_30_days=resolved_count,
        total_tickets=total,
    )


@router.get("/tickets", response_model=TaskListResponse)
async def get_my_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    type_filter: Optional[str] = Query(None, alias="type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tickets created by the current user"""
    base = select(Task).where(
        Task.tenant_id == current_user.tenant_id,
        Task.caller_id == current_user.id,
        Task.is_deleted == False,
    )

    if status_filter:
        base = base.where(Task.status == status_filter)
    if type_filter:
        base = base.where(Task.sys_class_name == type_filter)

    # Count
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    result = await db.execute(
        base.options(*_portal_task_load_options())
        .order_by(Task.sys_created_on.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    tasks = result.scalars().all()

    return TaskListResponse(total=total, tasks=tasks, page=page, page_size=page_size)


@router.get("/ticket/{ticket_id}", response_model=TaskResponse)
async def get_my_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single ticket (only if caller)"""
    result = await db.execute(
        select(Task)
        .options(*_portal_task_load_options())
        .where(
            Task.id == ticket_id,
            Task.tenant_id == current_user.tenant_id,
            Task.caller_id == current_user.id,
            Task.is_deleted == False,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return task


class PortalCreateTicket(BaseModel):
    """Simplified ticket creation for portal end-users"""
    sys_class_name: str = Field(default="incident", description="incident or request")
    short_description: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    urgency: str = Field(default="medium")
    impact: str = Field(default="medium")


@router.post("/tickets", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_my_ticket(
    data: PortalCreateTicket,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a ticket as an end-user (auto-sets caller, company, contact_type)"""
    # Calculate priority
    priority = PRIORITY_MATRIX.get(
        (data.urgency, data.impact), "medium"
    )

    # Generate ticket number
    prefix = Task.get_prefix_for_class(data.sys_class_name)
    count_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.sys_class_name == data.sys_class_name,
            Task.tenant_id == current_user.tenant_id,
        )
    )
    sequence = (count_result.scalar() or 0) + 1
    ticket_number = Task.generate_number(prefix, sequence)

    # Default to Servicedesk assignment group
    default_group = await db.execute(
        select(SupportGroup.id).where(
            SupportGroup.tenant_id == current_user.tenant_id,
            SupportGroup.name == "Servicedesk",
            SupportGroup.is_active == True,
        ).limit(1)
    )
    default_group_id = default_group.scalar_one_or_none()

    task = Task(
        sys_id=uuid_mod.uuid4(),
        number=ticket_number,
        tenant_id=current_user.tenant_id,
        company_id=current_user.primary_company_id,
        sys_class_name=data.sys_class_name,
        short_description=data.short_description,
        description=data.description,
        category=data.category,
        subcategory=data.subcategory,
        urgency=data.urgency,
        impact=data.impact,
        priority=priority,
        status="new" if data.sys_class_name == "incident" else "submitted",
        channel="portal",
        caller_id=current_user.id,
        opened_by_id=current_user.id,
        affected_user_id=current_user.id,
        assignment_group_id=default_group_id,
    )

    db.add(task)

    # Run before_create + before_submit rules (may modify task fields)
    await execute_rules("before_create", task, {}, db, current_user.tenant_id)
    await execute_rules("before_submit", task, {}, db, current_user.tenant_id)

    await db.flush()

    # Audit log
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        table_name="tasks",
        record_id=task.id,
        action="created",
        field_name="status",
        new_value=task.status,
        changed_by_id=current_user.id,
    )
    db.add(audit)
    await db.commit()

    # Run after_create + after_submit rules
    await execute_rules("after_create", task, {}, db, current_user.tenant_id)
    await execute_rules("after_submit", task, {}, db, current_user.tenant_id)

    # Re-fetch with relationships
    result = await db.execute(
        select(Task).options(*_portal_task_load_options()).where(Task.id == task.id)
    )
    return result.scalar_one()


class PortalAddComment(BaseModel):
    """Add a public comment to a ticket"""
    text: str = Field(..., min_length=1, max_length=4000)


@router.post("/ticket/{ticket_id}/comments", response_model=TaskResponse)
async def add_my_comment(
    ticket_id: UUID,
    data: PortalAddComment,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a public comment to own ticket"""
    result = await db.execute(
        select(Task).where(
            Task.id == ticket_id,
            Task.tenant_id == current_user.tenant_id,
            Task.caller_id == current_user.id,
            Task.is_deleted == False,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Append comment to JSON array (same structure as agent TaskForm: author, date, comment)
    existing = task.comments or []
    new_comment = {
        "author": f"{current_user.first_name} {current_user.last_name}",
        "date": datetime.now(timezone.utc).strftime("%m/%d/%Y, %I:%M:%S %p"),
        "comment": data.text,
        "source": "portal",
    }
    task.comments = existing + [new_comment]

    await db.commit()

    # Re-fetch with relationships
    refetch = await db.execute(
        select(Task).options(*_portal_task_load_options()).where(Task.id == task.id)
    )
    return refetch.scalar_one()


class CategoryResponse(BaseModel):
    """Category for portal display"""
    id: UUID
    name: str
    description: Optional[str] = None
    category_type: str
    parent_category_id: Optional[UUID] = None
    level: int
    icon: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/categories", response_model=list[CategoryResponse])
async def get_portal_categories(
    category_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get categories available in the portal"""
    query = select(Category).where(
        Category.tenant_id == current_user.tenant_id,
        Category.is_deleted == False,
    )

    if category_type:
        query = query.where(Category.category_type == category_type)

    result = await db.execute(query.order_by(Category.level, Category.sort_order, Category.name))
    return result.scalars().all()
