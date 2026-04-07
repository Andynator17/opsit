"""Incident management endpoints"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.incident import Incident
from app.models.support_group import group_members
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentAssign,
    IncidentResolve,
    IncidentClose,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


def generate_incident_number(tenant_id: UUID, count: int) -> str:
    """Generate unique incident number: INC-YYYYMMDD-XXXX"""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"INC-{today}-{count:04d}"


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new incident

    - **title**: Short description (5-255 chars)
    - **description**: Detailed description
    - **category**: Main category (required)
    - **urgency**: low, medium, high, critical
    - **impact**: low, medium, high, critical
    - **priority**: Automatically calculated from urgency + impact
    """

    # Calculate priority based on urgency and impact
    priority = Incident.calculate_priority(incident_data.urgency, incident_data.impact)

    # Generate unique incident number
    count_result = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    count = count_result.scalar() or 0
    incident_number = generate_incident_number(current_user.tenant_id, count + 1)

    # Create incident
    incident = Incident(
        tenant_id=current_user.tenant_id,
        company_id=incident_data.company_id,
        incident_number=incident_number,
        title=incident_data.title,
        description=incident_data.description,
        category=incident_data.category,
        subcategory=incident_data.subcategory,
        item=incident_data.item,
        urgency=incident_data.urgency,
        impact=incident_data.impact,
        priority=priority,
        status="new",
        # User fields (ITIL distinction)
        opened_by_id=incident_data.opened_by_id or current_user.id,
        caller_id=incident_data.caller_id,
        affected_user_id=incident_data.affected_user_id,
        reported_by_id=incident_data.reported_by_id or current_user.id,  # Deprecated
        reported_date=datetime.now(timezone.utc),
        contact_type=incident_data.contact_type,
        # Assignment
        assigned_group_id=incident_data.assigned_group_id,
        custom_fields=incident_data.custom_fields,
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    return incident


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    assigned_to_me: bool = Query(False, description="Show only tickets assigned to me"),
    assigned_to_my_groups: bool = Query(False, description="Show tickets assigned to my support groups"),
    assigned_to_id: Optional[UUID] = Query(None, description="Filter by assigned user"),
    assigned_group_id: Optional[UUID] = Query(None, description="Filter by assigned support group"),
    opened_by_id: Optional[UUID] = Query(None, description="Filter by opener"),
    caller_id: Optional[UUID] = Query(None, description="Filter by caller"),
    affected_user_id: Optional[UUID] = Query(None, description="Filter by affected user"),
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List incidents with filtering and pagination

    **Filters:**
    - status: new, assigned, in_progress, pending, resolved, closed
    - priority: low, medium, high, critical
    - category: Any category name
    - assigned_to_me: Show only tickets assigned to me directly
    - assigned_to_my_groups: Show tickets assigned to my support groups
    - assigned_to_id: Filter by assigned user
    - assigned_group_id: Filter by assigned support group
    - opened_by_id: Filter by who opened the ticket
    - caller_id: Filter by caller
    - affected_user_id: Filter by affected user
    - company_id: Filter by specific company
    - search: Search in title and description
    """

    # Base query
    query = select(Incident).where(
        Incident.tenant_id == current_user.tenant_id,
        Incident.is_deleted == False
    )

    # Apply filters
    if status_filter:
        query = query.where(Incident.status == status_filter)

    if priority:
        query = query.where(Incident.priority == priority)

    if category:
        query = query.where(Incident.category == category)

    if assigned_to_me:
        query = query.where(Incident.assigned_to_id == current_user.id)

    if assigned_to_my_groups:
        # Get all support groups the user is a member of
        group_result = await db.execute(
            select(group_members.c.group_id).where(
                group_members.c.user_id == current_user.id
            )
        )
        user_group_ids = [row[0] for row in group_result.all()]

        if user_group_ids:
            query = query.where(Incident.assigned_group_id.in_(user_group_ids))
        else:
            # User is not in any groups, return no results
            query = query.where(Incident.id == None)

    if assigned_to_id:
        query = query.where(Incident.assigned_to_id == assigned_to_id)

    if assigned_group_id:
        query = query.where(Incident.assigned_group_id == assigned_group_id)

    if opened_by_id:
        query = query.where(Incident.opened_by_id == opened_by_id)

    if caller_id:
        query = query.where(Incident.caller_id == caller_id)

    if affected_user_id:
        query = query.where(Incident.affected_user_id == affected_user_id)

    if company_id:
        query = query.where(Incident.company_id == company_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Incident.title.ilike(search_pattern),
                Incident.description.ilike(search_pattern),
                Incident.incident_number.ilike(search_pattern)
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Incident.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
    result = await db.execute(query)
    incidents = result.scalars().all()

    return IncidentListResponse(
        total=total,
        incidents=incidents,
        page=page,
        page_size=page_size
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single incident by ID"""

    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_update: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an incident

    All fields are optional. Only provided fields will be updated.
    Priority is automatically recalculated if urgency or impact changes.
    """

    # Fetch incident
    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Update fields
    update_data = incident_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    # Recalculate priority if urgency or impact changed
    if "urgency" in update_data or "impact" in update_data:
        incident.priority = Incident.calculate_priority(incident.urgency, incident.impact)

    await db.commit()
    await db.refresh(incident)

    return incident


@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: UUID,
    assignment: IncidentAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign an incident to a user or group

    Automatically changes status to 'assigned' if currently 'new'
    """

    # Fetch incident
    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Update assignment
    if assignment.assigned_to_id:
        incident.assigned_to_id = assignment.assigned_to_id
    if assignment.assigned_group_id:
        incident.assigned_group_id = assignment.assigned_group_id

    # Update status if needed
    if incident.status == "new":
        incident.status = "assigned"

    await db.commit()
    await db.refresh(incident)

    return incident


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: UUID,
    resolution: IncidentResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve an incident

    Changes status to 'resolved' and records resolution details
    """

    # Fetch incident
    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Check if incident can be resolved
    if incident.status in ["resolved", "closed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resolve incident with status '{incident.status}'"
        )

    # Update incident
    incident.status = "resolved"
    incident.resolved_by_id = current_user.id
    incident.resolved_date = datetime.now(timezone.utc)
    incident.resolution_notes = resolution.resolution_notes
    incident.resolution_code = resolution.resolution_code
    if resolution.root_cause:
        incident.root_cause = resolution.root_cause

    # Calculate resolution time
    if incident.reported_date:
        # Handle both timezone-aware and naive datetimes
        reported_date = incident.reported_date
        if reported_date.tzinfo is None:
            # If naive, assume UTC
            reported_date = reported_date.replace(tzinfo=timezone.utc)
        time_diff = datetime.now(timezone.utc) - reported_date
        incident.resolution_time_minutes = int(time_diff.total_seconds() / 60)

    await db.commit()
    await db.refresh(incident)

    return incident


@router.post("/{incident_id}/close", response_model=IncidentResponse)
async def close_incident(
    incident_id: UUID,
    closure: IncidentClose,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Close an incident

    Can only close resolved incidents. Changes status to 'closed'
    """

    # Fetch incident
    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Check if incident can be closed
    if incident.status != "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only resolved incidents can be closed"
        )

    # Update incident
    incident.status = "closed"
    incident.closed_by_id = current_user.id
    incident.closed_date = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(incident)

    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete an incident (admin only)

    Sets is_deleted flag to True instead of actually deleting the record
    """

    # Check admin permissions
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete incidents"
        )

    # Fetch incident
    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.tenant_id == current_user.tenant_id,
            Incident.is_deleted == False
        )
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Soft delete
    incident.is_deleted = True
    incident.deleted_at = datetime.now(timezone.utc)

    await db.commit()

    return None
