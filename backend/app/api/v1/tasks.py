"""
Task API endpoints - Generic ticket management (ServiceNow pattern)
Handles all ticket types: Incident, Request, Change, Problem, Task, Request Item
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rule_engine import execute_rules
from app.models.user import User
from app.models.task import Task
from app.models.support_group import SupportGroup, group_members
from app.models.audit_log import AuditLog
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskAssign,
    TaskResolve,
    TaskClose,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_load_options():
    """Standard selectinload options for TaskResponse serialization."""
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


async def _get_default_assignment_group_id(db: AsyncSession, tenant_id) -> Optional[UUID]:
    """Get the first active 'Servicedesk' support group for the tenant."""
    result = await db.execute(
        select(SupportGroup.id).where(
            SupportGroup.tenant_id == tenant_id,
            SupportGroup.name == "Servicedesk",
            SupportGroup.is_active == True,
        ).limit(1)
    )
    return result.scalar_one_or_none()


async def _refetch_task(db: AsyncSession, task_id) -> Task:
    """Re-fetch a task with all relationships for response serialization."""
    result = await db.execute(
        select(Task).options(*_task_load_options()).where(Task.id == task_id)
    )
    return result.scalar_one()


async def _resolve_display_name(db: AsyncSession, field_name: str, value) -> str:
    """Resolve a UUID foreign key to a human-readable display name for audit logs."""
    if value is None:
        return None
    str_val = str(value)
    if field_name in ("assigned_to_id", "caller_id", "affected_user_id", "opened_by_id"):
        result = await db.execute(select(User.first_name, User.last_name).where(User.id == value))
        row = result.first()
        return f"{row[0]} {row[1]}" if row else str_val
    if field_name == "assignment_group_id":
        from app.models.support_group import SupportGroup
        result = await db.execute(select(SupportGroup.name).where(SupportGroup.id == value))
        row = result.first()
        return row[0] if row else str_val
    if field_name == "company_id":
        from app.models.company import Company
        result = await db.execute(select(Company.name).where(Company.id == value))
        row = result.first()
        return row[0] if row else str_val
    return str_val


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task (any type: incident, request, change, problem, etc.)

    The system will:
    - Auto-generate ticket number (e.g., INC000000001, REQ000000001)
    - Calculate priority from urgency + impact
    - Set initial status based on ticket type
    - Auto-fill opened_by if not provided
    """

    # Calculate priority
    priority = Task.calculate_priority(task_data.urgency, task_data.impact)

    # Determine initial status based on class
    initial_status_map = {
        "incident": "new",
        "request": "submitted",
        "change": "draft",
        "problem": "new",
        "task": "pending",
        "approval": "pending",
        "request_item": "pending",
    }
    initial_status = initial_status_map.get(task_data.sys_class_name, "new")

    # Generate ticket number
    # Get the last number for this ticket class
    prefix = Task.get_prefix_for_class(task_data.sys_class_name)
    result = await db.execute(
        select(func.count(Task.id)).where(
            Task.sys_class_name == task_data.sys_class_name,
            Task.tenant_id == current_user.tenant_id
        )
    )
    sequence = (result.scalar() or 0) + 1
    ticket_number = Task.generate_number(prefix, sequence)

    # Default to Servicedesk if no assignment group provided
    assignment_group_id = task_data.assignment_group_id
    if not assignment_group_id:
        assignment_group_id = await _get_default_assignment_group_id(db, current_user.tenant_id)

    # Create task
    import uuid
    task = Task(
        sys_id=uuid.uuid4(),
        number=ticket_number,
        sys_class_name=task_data.sys_class_name,
        tenant_id=current_user.tenant_id,
        company_id=task_data.company_id,
        short_description=task_data.short_description,
        description=task_data.description,
        category=task_data.category,
        subcategory=task_data.subcategory,
        urgency=task_data.urgency,
        impact=task_data.impact,
        priority=priority,
        status=initial_status,
        channel=task_data.channel,
        opened_by_id=task_data.opened_by_id or current_user.id,
        caller_id=task_data.caller_id,
        affected_user_id=task_data.affected_user_id,
        assignment_group_id=assignment_group_id,
        assigned_to_id=task_data.assigned_to_id,
        custom_fields=task_data.custom_fields,
        is_active=True,
        is_deleted=False,
    )

    db.add(task)

    # Run before_create + before_submit rules (may modify task fields)
    await execute_rules("before_create", task, {}, db, current_user.tenant_id)
    await execute_rules("before_submit", task, {}, db, current_user.tenant_id)

    await db.flush()  # Generate task.id before referencing it in audit log

    # Audit: record creation
    audit_entry = AuditLog(
        tenant_id=current_user.tenant_id,
        table_name="tasks",
        record_id=task.id,
        action="create",
        field_name=None,
        old_value=None,
        new_value=ticket_number,
        changed_by_id=current_user.id,
    )
    db.add(audit_entry)

    await db.commit()

    # Run after_create + after_submit rules
    await execute_rules("after_create", task, {}, db, current_user.tenant_id)
    await execute_rules("after_submit", task, {}, db, current_user.tenant_id)

    return await _refetch_task(db, task.id)


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    sys_class_name: Optional[str] = Query(None, description="Filter by ticket type (incident, request, etc.)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    assigned_to_me: bool = Query(False, description="Show only tickets assigned to me"),
    assigned_to_my_groups: bool = Query(False, description="Show tickets assigned to my support groups"),
    assigned_to_id: Optional[UUID] = Query(None, description="Filter by assigned user"),
    assignment_group_id: Optional[UUID] = Query(None, description="Filter by assigned support group"),
    opened_by_id: Optional[UUID] = Query(None, description="Filter by opener"),
    caller_id: Optional[UUID] = Query(None, description="Filter by caller"),
    affected_user_id: Optional[UUID] = Query(None, description="Filter by affected user"),
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    search: Optional[str] = Query(None, description="Search in title/description/number"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List tasks with filtering and pagination

    **Filters:**
    - sys_class_name: incident, request, change, problem, task, request_item
    - status: varies by ticket type
    - priority: low, medium, high, critical
    - assigned_to_me: Show only tickets assigned to me directly
    - assigned_to_my_groups: Show tickets assigned to my support groups
    - search: Search in number, title, description
    """

    # Base query with eager loading of relationships
    query = select(Task).options(
        *_task_load_options()
    ).where(
        Task.tenant_id == current_user.tenant_id,
        Task.is_deleted == False
    )

    # Apply filters
    if sys_class_name:
        query = query.where(Task.sys_class_name == sys_class_name)

    if status:
        query = query.where(Task.status == status)

    if priority:
        query = query.where(Task.priority == priority)

    if category:
        query = query.where(Task.category == category)

    if assigned_to_me:
        query = query.where(Task.assigned_to_id == current_user.id)

    if assigned_to_my_groups:
        # Get all support groups the user is a member of
        group_result = await db.execute(
            select(group_members.c.group_id).where(
                group_members.c.user_id == current_user.id
            )
        )
        user_group_ids = [row[0] for row in group_result.all()]

        if user_group_ids:
            query = query.where(Task.assignment_group_id.in_(user_group_ids))
        else:
            # User is not in any groups, return no results
            query = query.where(Task.id == None)

    if assigned_to_id:
        query = query.where(Task.assigned_to_id == assigned_to_id)

    if assignment_group_id:
        query = query.where(Task.assignment_group_id == assignment_group_id)

    if opened_by_id:
        query = query.where(Task.opened_by_id == opened_by_id)

    if caller_id:
        query = query.where(Task.caller_id == caller_id)

    if affected_user_id:
        query = query.where(Task.affected_user_id == affected_user_id)

    if company_id:
        query = query.where(Task.company_id == company_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Task.short_description.ilike(search_pattern),
                Task.description.ilike(search_pattern),
                Task.number.ilike(search_pattern)
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Task.sys_created_on.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        total=total,
        tasks=tasks,
        page=page,
        page_size=page_size
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task by ID"""
    result = await db.execute(
        select(Task).options(
            *_task_load_options()
        ).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Capture old values for rule engine (before applying changes)
    update_data = task_data.model_dump(exclude_unset=True)
    old_values = {f: getattr(task, f, None) for f in update_data.keys()}

    # Update fields with audit tracking
    audited_fields = {
        "status", "assignment_group_id", "assigned_to_id", "priority",
        "urgency", "impact", "resolution", "short_description", "description",
        "category", "subcategory", "company_id", "caller_id", "affected_user_id",
    }

    # Fields that contain UUIDs needing name resolution
    uuid_fields = {
        "assigned_to_id", "assignment_group_id", "caller_id",
        "affected_user_id", "company_id",
    }

    for field, value in update_data.items():
        old_value = getattr(task, field, None)
        if field in audited_fields and str(old_value) != str(value):
            if field in uuid_fields:
                display_old = await _resolve_display_name(db, field, old_value)
                display_new = await _resolve_display_name(db, field, value)
            else:
                display_old = str(old_value) if old_value is not None else None
                display_new = str(value) if value is not None else None
            db.add(AuditLog(
                tenant_id=current_user.tenant_id,
                table_name="tasks",
                record_id=task.id,
                action="update",
                field_name=field,
                old_value=display_old,
                new_value=display_new,
                changed_by_id=current_user.id,
            ))
        setattr(task, field, value)

    # Recalculate priority if urgency or impact changed
    if 'urgency' in update_data or 'impact' in update_data:
        new_priority = Task.calculate_priority(task.urgency, task.impact)
        if task.priority != new_priority:
            db.add(AuditLog(
                tenant_id=current_user.tenant_id,
                table_name="tasks",
                record_id=task.id,
                action="update",
                field_name="priority",
                old_value=task.priority,
                new_value=new_priority,
                changed_by_id=current_user.id,
            ))
            task.priority = new_priority

    task.last_modified_by_id = current_user.id
    task.last_modified_at = datetime.now(timezone.utc)

    # Run before_update + before_submit rules (may modify task fields further)
    await execute_rules("before_update", task, old_values, db, current_user.tenant_id)
    await execute_rules("before_submit", task, old_values, db, current_user.tenant_id)

    await db.commit()

    # Run after_update + after_submit rules
    await execute_rules("after_update", task, old_values, db, current_user.tenant_id)
    await execute_rules("after_submit", task, old_values, db, current_user.tenant_id)

    return await _refetch_task(db, task.id)


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: UUID,
    assign_data: TaskAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign a task to a user or group"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Track reassignment
    if task.assigned_to_id or task.assignment_group_id:
        task.reassignment_count += 1

    # Update assignment with audit (resolve names for readability)
    old_status = task.status
    if assign_data.assigned_to_id is not None:
        old_display = await _resolve_display_name(db, "assigned_to_id", task.assigned_to_id)
        new_display = await _resolve_display_name(db, "assigned_to_id", assign_data.assigned_to_id)
        task.assigned_to_id = assign_data.assigned_to_id
        db.add(AuditLog(
            tenant_id=current_user.tenant_id, table_name="tasks", record_id=task.id,
            action="update", field_name="assigned_to_id",
            old_value=old_display, new_value=new_display,
            changed_by_id=current_user.id,
        ))
    if assign_data.assignment_group_id is not None:
        old_display = await _resolve_display_name(db, "assignment_group_id", task.assignment_group_id)
        new_display = await _resolve_display_name(db, "assignment_group_id", assign_data.assignment_group_id)
        task.assignment_group_id = assign_data.assignment_group_id
        db.add(AuditLog(
            tenant_id=current_user.tenant_id, table_name="tasks", record_id=task.id,
            action="update", field_name="assignment_group_id",
            old_value=old_display, new_value=new_display,
            changed_by_id=current_user.id,
        ))

    # Update status if new
    if task.status == "new":
        task.status = "assigned"
    elif task.status == "submitted":
        task.status = "approved"  # For requests

    if task.status != old_status:
        db.add(AuditLog(
            tenant_id=current_user.tenant_id, table_name="tasks", record_id=task.id,
            action="update", field_name="status",
            old_value=old_status, new_value=task.status,
            changed_by_id=current_user.id,
        ))

    task.last_modified_by_id = current_user.id
    task.last_modified_at = datetime.now(timezone.utc)

    await db.commit()

    return await _refetch_task(db, task.id)


@router.post("/{task_id}/resolve", response_model=TaskResponse)
async def resolve_task(
    task_id: UUID,
    resolve_data: TaskResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resolve a task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update resolution with audit
    old_status = task.status
    task.status = "resolved"
    task.resolved_by_id = current_user.id
    task.resolved_at = datetime.now(timezone.utc)
    task.resolution = resolve_data.resolution
    task.resolution_reason = resolve_data.resolution_reason

    db.add(AuditLog(
        tenant_id=current_user.tenant_id, table_name="tasks", record_id=task.id,
        action="update", field_name="status",
        old_value=old_status, new_value="resolved",
        changed_by_id=current_user.id,
    ))
    db.add(AuditLog(
        tenant_id=current_user.tenant_id, table_name="tasks", record_id=task.id,
        action="update", field_name="resolution",
        old_value=None, new_value=resolve_data.resolution,
        changed_by_id=current_user.id,
    ))

    if resolve_data.root_cause:
        task.root_cause = resolve_data.root_cause
    if resolve_data.workaround:
        task.workaround = resolve_data.workaround

    task.last_modified_by_id = current_user.id
    task.last_modified_at = datetime.now(timezone.utc)

    await db.commit()

    return await _refetch_task(db, task.id)


@router.post("/{task_id}/close", response_model=TaskResponse)
async def close_task(
    task_id: UUID,
    close_data: TaskClose,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Close a task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Can only close resolved tasks
    if task.status not in ["resolved", "fulfilled", "complete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot close task with status '{task.status}'. Must be resolved first."
        )

    old_status = task.status
    task.status = "closed"
    task.closed_by_id = current_user.id
    task.closed_at = datetime.now(timezone.utc)
    task.close_notes = close_data.close_notes

    db.add(AuditLog(
        tenant_id=current_user.tenant_id, table_name="tasks", record_id=task.id,
        action="update", field_name="status",
        old_value=old_status, new_value="closed",
        changed_by_id=current_user.id,
    ))

    task.last_modified_by_id = current_user.id
    task.last_modified_at = datetime.now(timezone.utc)

    await db.commit()

    return await _refetch_task(db, task.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id,
            Task.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Soft delete
    task.is_deleted = True
    task.deleted_at = datetime.now(timezone.utc)

    await db.commit()

    return None
