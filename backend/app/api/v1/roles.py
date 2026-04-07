"""Roles API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.role import Role
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse
)

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=RoleListResponse)
async def get_roles(
    module: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of roles

    Filter by module (incident, request, task, etc.) or level (read, read_create, agent, admin)
    """
    # Build query
    query = select(Role).where(
        and_(
            Role.tenant_id == current_user.tenant_id,
            Role.is_deleted == False
        )
    )

    if module:
        query = query.where(Role.module == module)
    if level:
        query = query.where(Role.level == level)

    # Get total count
    count_result = await db.execute(
        select(Role).where(
            and_(
                Role.tenant_id == current_user.tenant_id,
                Role.is_deleted == False
            )
        )
    )
    total = len(count_result.scalars().all())

    # Get roles with pagination
    query = query.order_by(Role.module, Role.level).offset(skip).limit(limit)
    result = await db.execute(query)
    roles = result.scalars().all()

    return RoleListResponse(total=total, roles=roles)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get role by ID"""
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.tenant_id == current_user.tenant_id,
                Role.is_deleted == False
            )
        )
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return role


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new role (admin only)"""

    # Check if code already exists
    existing = await db.execute(
        select(Role).where(
            and_(
                Role.code == role_data.code,
                Role.tenant_id == current_user.tenant_id,
                Role.is_deleted == False
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with code '{role_data.code}' already exists"
        )

    # Create role
    role = Role(
        tenant_id=current_user.tenant_id,
        **role_data.model_dump()
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    return role


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update role

    System roles cannot be modified. Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update roles"
        )

    # Get role
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.tenant_id == current_user.tenant_id,
                Role.is_deleted == False
            )
        )
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System roles cannot be modified"
        )

    # Update role
    update_data = role_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)

    await db.commit()
    await db.refresh(role)

    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete role (soft delete)

    System roles cannot be deleted. Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete roles"
        )

    # Get role
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.tenant_id == current_user.tenant_id,
                Role.is_deleted == False
            )
        )
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System roles cannot be deleted"
        )

    # Soft delete
    role.is_deleted = True
    await db.commit()

    return None
