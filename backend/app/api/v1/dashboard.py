"""Dashboard and statistics endpoints — uses central Task model"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.support_group import group_members
from pydantic import BaseModel


class TicketStats(BaseModel):
    """Ticket statistics"""
    total: int
    new: int
    assigned: int
    in_progress: int
    pending: int
    resolved: int
    closed: int


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    incidents: TicketStats
    requests: TicketStats
    my_open_incidents: int
    my_open_requests: int
    pending_approvals: int


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def _count_by_status(db: AsyncSession, tenant_id, sys_class_name: str) -> dict:
    """Count tasks grouped by status for a given ticket type. Returns dict of status->count."""
    result = await db.execute(
        select(Task.status, func.count(Task.id))
        .where(
            Task.tenant_id == tenant_id,
            Task.sys_class_name == sys_class_name,
            Task.is_deleted == False,
        )
        .group_by(Task.status)
    )
    return dict(result.all())


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics using central Task model"""

    # Get incident counts grouped by status (single query instead of 7)
    inc_counts = await _count_by_status(db, current_user.tenant_id, "incident")

    # Get request counts grouped by status (single query instead of 7)
    req_counts = await _count_by_status(db, current_user.tenant_id, "request")

    # My assigned open incidents
    my_inc = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == current_user.tenant_id,
            Task.sys_class_name == "incident",
            Task.assigned_to_id == current_user.id,
            Task.status.in_(["assigned", "in_progress", "pending"]),
            Task.is_deleted == False,
        )
    )

    # My assigned open requests
    my_req = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == current_user.tenant_id,
            Task.sys_class_name == "request",
            Task.assigned_to_id == current_user.id,
            Task.status.in_(["assigned", "in_progress", "pending"]),
            Task.is_deleted == False,
        )
    )

    # Pending approvals
    pending_approvals_count = 0
    if current_user.is_admin or current_user.is_support_agent:
        pa = await db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == current_user.tenant_id,
                Task.sys_class_name == "approval",
                Task.status.in_(["new", "assigned"]),
                Task.is_deleted == False,
            )
        )
        pending_approvals_count = pa.scalar() or 0

    return DashboardStats(
        incidents=TicketStats(
            total=sum(inc_counts.values()),
            new=inc_counts.get("new", 0),
            assigned=inc_counts.get("assigned", 0),
            in_progress=inc_counts.get("in_progress", 0),
            pending=inc_counts.get("pending", 0),
            resolved=inc_counts.get("resolved", 0),
            closed=inc_counts.get("closed", 0),
        ),
        requests=TicketStats(
            total=sum(req_counts.values()),
            new=req_counts.get("new", 0),
            assigned=req_counts.get("assigned", 0),
            in_progress=req_counts.get("in_progress", 0),
            pending=req_counts.get("pending", 0),
            resolved=req_counts.get("resolved", 0),
            closed=req_counts.get("closed", 0),
        ),
        my_open_incidents=my_inc.scalar() or 0,
        my_open_requests=my_req.scalar() or 0,
        pending_approvals=pending_approvals_count,
    )


class AgentDashboardStats(BaseModel):
    """Agent dashboard statistics"""
    new_unassigned_incidents: int
    my_approvals_open: int
    my_requests_open: int
    sla_breach: int
    support_group_incidents: int
    support_group_changes: int
    support_group_tasks: int
    my_incidents: int
    my_changes: int
    my_tasks: int


class TicketSummary(BaseModel):
    """Ticket summary for overview console"""
    id: UUID
    ticket_number: str
    ticket_type: str
    title: str
    priority: str
    status: str
    assigned_to_name: Optional[str] = None
    support_group_name: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    sla_breach: bool = False

    class Config:
        from_attributes = True


class OverviewConsoleResponse(BaseModel):
    """Overview console with tickets"""
    total: int
    tickets: List[TicketSummary]


@router.get("/stats/agent", response_model=AgentDashboardStats)
async def get_agent_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent dashboard statistics using central Task model"""

    tenant_id = current_user.tenant_id
    open_statuses = ["new", "assigned", "in_progress", "pending"]

    # Get user's support groups
    sg_result = await db.execute(
        select(group_members.c.group_id).where(
            group_members.c.user_id == current_user.id
        )
    )
    user_support_groups = [row[0] for row in sg_result.fetchall()]

    # 1. New/Unassigned Incidents
    new_unassigned = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id,
            Task.sys_class_name == "incident",
            Task.is_deleted == False,
            Task.assigned_to_id == None,
            Task.status.in_(["new", "assigned"]),
        )
    )

    # 2. My Approvals (pending approval tasks)
    my_approvals_open = 0
    if current_user.is_admin or current_user.is_support_agent:
        ma = await db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == tenant_id,
                Task.sys_class_name == "approval",
                Task.status.in_(["new", "assigned"]),
                Task.is_deleted == False,
            )
        )
        my_approvals_open = ma.scalar() or 0

    # 3. My Requests (Open) - requests opened by me
    my_req = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id,
            Task.sys_class_name == "request",
            Task.is_deleted == False,
            Task.opened_by_id == current_user.id,
            Task.status.in_(open_statuses),
        )
    )

    # 4. SLA Breach - tasks past due
    now = datetime.now(timezone.utc)
    sla_breach_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id,
            Task.is_deleted == False,
            Task.sla_target_resolve < now,
            ~Task.status.in_(["resolved", "closed", "cancelled"]),
        )
    )

    # 5-7. Support Group tickets (incidents, changes, tasks)
    sg_incidents = 0
    sg_changes = 0
    sg_tasks = 0
    if user_support_groups:
        sg_result = await db.execute(
            select(Task.sys_class_name, func.count(Task.id))
            .where(
                Task.tenant_id == tenant_id,
                Task.is_deleted == False,
                Task.assignment_group_id.in_(user_support_groups),
                ~Task.status.in_(["resolved", "closed", "cancelled"]),
            )
            .group_by(Task.sys_class_name)
        )
        sg_counts = dict(sg_result.all())
        sg_incidents = sg_counts.get("incident", 0)
        sg_changes = sg_counts.get("change", 0)
        sg_tasks = sg_counts.get("task", 0)

    # 8-10. My assigned tickets (incidents, changes, tasks)
    my_result = await db.execute(
        select(Task.sys_class_name, func.count(Task.id))
        .where(
            Task.tenant_id == tenant_id,
            Task.is_deleted == False,
            Task.assigned_to_id == current_user.id,
            ~Task.status.in_(["resolved", "closed", "cancelled"]),
        )
        .group_by(Task.sys_class_name)
    )
    my_counts = dict(my_result.all())

    return AgentDashboardStats(
        new_unassigned_incidents=new_unassigned.scalar() or 0,
        my_approvals_open=my_approvals_open,
        my_requests_open=my_req.scalar() or 0,
        sla_breach=sla_breach_result.scalar() or 0,
        support_group_incidents=sg_incidents,
        support_group_changes=sg_changes,
        support_group_tasks=sg_tasks,
        my_incidents=my_counts.get("incident", 0),
        my_changes=my_counts.get("change", 0),
        my_tasks=my_counts.get("task", 0),
    )


@router.get("/overview", response_model=OverviewConsoleResponse)
async def get_overview_console(
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overview console - all tickets from user's support groups"""

    # Get user's support groups
    sg_result = await db.execute(
        select(group_members.c.group_id).where(
            group_members.c.user_id == current_user.id
        )
    )
    user_support_groups = [row[0] for row in sg_result.fetchall()]

    if not user_support_groups:
        return OverviewConsoleResponse(total=0, tickets=[])

    # Build query filters
    task_filters = [
        Task.tenant_id == current_user.tenant_id,
        Task.is_deleted == False,
        Task.assignment_group_id.in_(user_support_groups),
        ~Task.status.in_(["resolved", "closed", "cancelled", "fulfilled"]),
    ]

    if ticket_type:
        task_filters.append(Task.sys_class_name == ticket_type)
    if priority:
        task_filters.append(Task.priority == priority)
    if status:
        task_filters.append(Task.status == status)

    # Fetch tasks with relationships
    tasks_query = (
        select(Task)
        .options(
            selectinload(Task.assigned_to),
            selectinload(Task.assignment_group),
        )
        .where(and_(*task_filters))
        .order_by(Task.sys_created_on.desc())
        .limit(limit)
        .offset(skip)
    )
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    # Get total count
    count_query = select(func.count(Task.id)).where(and_(*task_filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Convert to TicketSummary
    now = datetime.now(timezone.utc)
    tickets = []
    for task in tasks:
        assigned_to_name = None
        if task.assigned_to:
            assigned_to_name = f"{task.assigned_to.first_name} {task.assigned_to.last_name}"

        support_group_name = None
        if task.assignment_group:
            support_group_name = task.assignment_group.name

        sla_breach = False
        if task.sla_target_resolve:
            target = task.sla_target_resolve
            if target.tzinfo is None:
                target = target.replace(tzinfo=timezone.utc)
            sla_breach = target < now

        tickets.append(TicketSummary(
            id=task.id,
            ticket_number=task.number,
            ticket_type=task.sys_class_name,
            title=task.short_description,
            priority=task.priority,
            status=task.status,
            assigned_to_name=assigned_to_name,
            support_group_name=support_group_name,
            created_at=task.sys_created_on,
            due_date=task.sla_target_resolve,
            sla_breach=sla_breach,
        ))

    return OverviewConsoleResponse(total=total, tickets=tickets)
