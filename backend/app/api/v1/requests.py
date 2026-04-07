"""Service Request management endpoints"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.request import Request
from app.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestResponse,
    RequestListResponse,
    RequestApprove,
    RequestReject,
    RequestAssign,
    RequestFulfill,
    RequestClose,
)

router = APIRouter(prefix="/requests", tags=["requests"])


def generate_request_number(tenant_id: UUID, count: int) -> str:
    """Generate unique request number: REQ-YYYYMMDD-XXXX"""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"REQ-{today}-{count:04d}"


@router.post("/", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: RequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new service request

    - **title**: Short description
    - **description**: Detailed description
    - **category**: Request category
    - **urgency**: low, medium, high, critical
    - **requires_approval**: Whether approval is needed
    """

    # Priority is same as urgency for requests (simpler than incidents)
    priority = request_data.urgency

    # Generate unique request number
    count_result = await db.execute(
        select(func.count(Request.id)).where(
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    count = count_result.scalar() or 0
    request_number = generate_request_number(current_user.tenant_id, count + 1)

    # Determine initial status
    initial_status = "pending_approval" if request_data.requires_approval else "submitted"

    # Create request
    service_request = Request(
        tenant_id=current_user.tenant_id,
        company_id=request_data.company_id,
        request_number=request_number,
        title=request_data.title,
        description=request_data.description,
        category=request_data.category,
        subcategory=request_data.subcategory,
        catalog_item=request_data.catalog_item,
        urgency=request_data.urgency,
        priority=priority,
        status=initial_status,
        requested_by_id=request_data.requested_by_id or current_user.id,
        requested_for_id=request_data.requested_for_id,
        requested_date=datetime.now(timezone.utc),
        contact_type=request_data.contact_type,
        requires_approval=request_data.requires_approval,
        business_justification=request_data.business_justification,
        quantity=request_data.quantity,
        custom_fields=request_data.custom_fields,
    )

    db.add(service_request)
    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.get("/", response_model=RequestListResponse)
async def list_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    my_requests: bool = Query(False, description="Show only my requests"),
    pending_approval: bool = Query(False, description="Show only pending approvals"),
    company_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List service requests with filtering and pagination

    **Filters:**
    - status: submitted, pending_approval, approved, in_progress, fulfilled, closed
    - priority: low, medium, high, critical
    - category: Any category name
    - my_requests: Show only requests I created
    - pending_approval: Show only requests awaiting approval (for approvers)
    """

    # Base query
    query = select(Request).where(
        Request.tenant_id == current_user.tenant_id,
        Request.is_deleted == False
    )

    # Apply filters
    if status_filter:
        query = query.where(Request.status == status_filter)

    if priority:
        query = query.where(Request.priority == priority)

    if category:
        query = query.where(Request.category == category)

    if my_requests:
        query = query.where(Request.requested_by_id == current_user.id)

    if pending_approval:
        query = query.where(Request.status == "pending_approval")

    if company_id:
        query = query.where(Request.company_id == company_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Request.title.ilike(search_pattern),
                Request.description.ilike(search_pattern),
                Request.request_number.ilike(search_pattern)
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(Request.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute
    result = await db.execute(query)
    requests = result.scalars().all()

    return RequestListResponse(
        total=total,
        requests=requests,
        page=page,
        page_size=page_size
    )


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single request by ID"""

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    return service_request


@router.patch("/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: UUID,
    request_update: RequestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a request"""

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Update fields
    update_data = request_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service_request, field, value)

    # If urgency changed, update priority
    if "urgency" in update_data:
        service_request.priority = service_request.urgency

    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.post("/{request_id}/approve", response_model=RequestResponse)
async def approve_request(
    request_id: UUID,
    approval: RequestApprove,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a request (admin/manager only)

    Changes status from pending_approval to approved
    """

    # Check permissions (could add manager check here)
    if not (current_user.is_admin or current_user.is_support_agent):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and agents can approve requests"
        )

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if service_request.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status '{service_request.status}'"
        )

    # Approve
    service_request.status = "approved"
    service_request.approved_by_id = current_user.id
    service_request.approved_date = datetime.now(timezone.utc)
    service_request.approval_notes = approval.approval_notes

    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.post("/{request_id}/reject", response_model=RequestResponse)
async def reject_request(
    request_id: UUID,
    rejection: RequestReject,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a request (admin/manager only)"""

    if not (current_user.is_admin or current_user.is_support_agent):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and agents can reject requests"
        )

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if service_request.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject request with status '{service_request.status}'"
        )

    # Reject
    service_request.status = "rejected"
    service_request.rejection_reason = rejection.rejection_reason

    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.post("/{request_id}/assign", response_model=RequestResponse)
async def assign_request(
    request_id: UUID,
    assignment: RequestAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign a request to a user or group"""

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Update assignment
    if assignment.assigned_to_id:
        service_request.assigned_to_id = assignment.assigned_to_id
    if assignment.assigned_group_id:
        service_request.assigned_group_id = assignment.assigned_group_id

    # Update status if needed
    if service_request.status in ["submitted", "approved"]:
        service_request.status = "in_progress"

    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.post("/{request_id}/fulfill", response_model=RequestResponse)
async def fulfill_request(
    request_id: UUID,
    fulfillment: RequestFulfill,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a request as fulfilled"""

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if service_request.status in ["fulfilled", "closed", "cancelled", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot fulfill request with status '{service_request.status}'"
        )

    # Fulfill
    service_request.status = "fulfilled"
    service_request.fulfilled_by_id = current_user.id
    service_request.fulfilled_date = datetime.now(timezone.utc)
    service_request.fulfillment_notes = fulfillment.fulfillment_notes

    # Calculate fulfillment time
    if service_request.requested_date:
        requested_date = service_request.requested_date
        if requested_date.tzinfo is None:
            requested_date = requested_date.replace(tzinfo=timezone.utc)
        time_diff = datetime.now(timezone.utc) - requested_date
        service_request.fulfillment_time_minutes = int(time_diff.total_seconds() / 60)

    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.post("/{request_id}/close", response_model=RequestResponse)
async def close_request(
    request_id: UUID,
    closure: RequestClose,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Close a request (can only close fulfilled requests)"""

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if service_request.status != "fulfilled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only fulfilled requests can be closed"
        )

    # Close
    service_request.status = "closed"
    service_request.closed_by_id = current_user.id
    service_request.closed_date = datetime.now(timezone.utc)
    service_request.closure_notes = closure.closure_notes

    await db.commit()
    await db.refresh(service_request)

    return service_request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a request (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete requests"
        )

    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.tenant_id == current_user.tenant_id,
            Request.is_deleted == False
        )
    )
    service_request = result.scalar_one_or_none()

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Soft delete
    service_request.is_deleted = True
    service_request.deleted_at = datetime.now(timezone.utc)

    await db.commit()

    return None
