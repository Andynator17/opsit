"""Department management endpoints"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentListResponse,
)

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new department (admin only)"""
    dept = Department(
        tenant_id=current_user.tenant_id,
        company_id=data.company_id,
        name=data.name,
        description=data.description,
        manager_id=data.manager_id,
        parent_department_id=data.parent_department_id,
    )
    db.add(dept)
    await db.commit()

    # Re-fetch with relationships for response serialization
    result = await db.execute(
        select(Department)
        .options(selectinload(Department.company), selectinload(Department.manager))
        .where(Department.id == dept.id, Department.tenant_id == current_user.tenant_id)
    )
    return result.scalar_one()


@router.get("/", response_model=DepartmentListResponse)
async def list_departments(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all departments"""
    query = (
        select(Department)
        .options(selectinload(Department.company), selectinload(Department.manager))
        .where(
            Department.tenant_id == current_user.tenant_id,
            Department.is_deleted == False,
        )
    )

    if company_id:
        query = query.where(Department.company_id == company_id)

    query = query.order_by(Department.name)
    result = await db.execute(query)
    departments = result.scalars().all()

    return DepartmentListResponse(total=len(departments), departments=departments)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single department"""
    result = await db.execute(
        select(Department)
        .options(selectinload(Department.company), selectinload(Department.manager))
        .where(
            Department.id == department_id,
            Department.tenant_id == current_user.tenant_id,
            Department.is_deleted == False,
        )
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return dept


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a department (admin only)"""
    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == current_user.tenant_id,
            Department.is_deleted == False,
        )
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dept, field, value)

    await db.commit()

    # Re-fetch with relationships for response serialization
    result = await db.execute(
        select(Department)
        .options(selectinload(Department.company), selectinload(Department.manager))
        .where(Department.id == department_id, Department.tenant_id == current_user.tenant_id)
    )
    return result.scalar_one()


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a department (admin only)"""
    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == current_user.tenant_id,
            Department.is_deleted == False,
        )
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    dept.is_deleted = True
    dept.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None
