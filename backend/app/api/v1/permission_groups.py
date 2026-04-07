"""Permission Groups API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.role import Role
from app.models.permission_group import PermissionGroup
from app.schemas.permission_group import (
    PermissionGroupCreate,
    PermissionGroupUpdate,
    PermissionGroupResponse,
    PermissionGroupListResponse,
    PermissionGroupAddMembers,
    PermissionGroupAddRoles
)

router = APIRouter(prefix="/permission-groups", tags=["permission-groups"])


@router.get("/", response_model=PermissionGroupListResponse)
async def get_permission_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of permission groups"""
    # Get total count
    count_result = await db.execute(
        select(PermissionGroup).where(
            and_(
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    total = len(count_result.scalars().all())

    # Get permission groups with pagination
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
        .order_by(PermissionGroup.name)
        .offset(skip)
        .limit(limit)
    )
    permission_groups = result.scalars().all()

    return PermissionGroupListResponse(total=total, permission_groups=permission_groups)


@router.get("/{group_id}", response_model=PermissionGroupResponse)
async def get_permission_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get permission group by ID"""
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    return group


@router.post("/", response_model=PermissionGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_group(
    group_data: PermissionGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new permission group (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create permission groups"
        )

    # Create permission group
    group = PermissionGroup(
        tenant_id=current_user.tenant_id,
        name=group_data.name,
        description=group_data.description
    )

    # Add initial members
    if group_data.member_ids:
        members_result = await db.execute(
            select(User).where(
                and_(
                    User.id.in_(group_data.member_ids),
                    User.tenant_id == current_user.tenant_id,
                    User.is_deleted == False
                )
            )
        )
        group.members = list(members_result.scalars().all())

    # Add initial roles
    if group_data.role_ids:
        roles_result = await db.execute(
            select(Role).where(
                and_(
                    Role.id.in_(group_data.role_ids),
                    Role.tenant_id == current_user.tenant_id,
                    Role.is_deleted == False
                )
            )
        )
        group.roles = list(roles_result.scalars().all())

    db.add(group)
    await db.commit()
    await db.refresh(group, ["members", "roles"])

    return group


@router.patch("/{group_id}", response_model=PermissionGroupResponse)
async def update_permission_group(
    group_id: UUID,
    group_data: PermissionGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update permission group (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update permission groups"
        )

    # Get group
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    # Update group
    update_data = group_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)

    return group


@router.post("/{group_id}/members", response_model=PermissionGroupResponse)
async def add_members_to_permission_group(
    group_id: UUID,
    data: PermissionGroupAddMembers,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add members to permission group (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add members to permission groups"
        )

    # Get group
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    # Get users to add
    users_result = await db.execute(
        select(User).where(
            and_(
                User.id.in_(data.user_ids),
                User.tenant_id == current_user.tenant_id,
                User.is_deleted == False
            )
        )
    )
    users = users_result.scalars().all()

    # Add new members (avoiding duplicates)
    existing_ids = {m.id for m in group.members}
    for user in users:
        if user.id not in existing_ids:
            group.members.append(user)

    await db.commit()
    await db.refresh(group)

    return group


@router.delete("/{group_id}/members/{user_id}", response_model=PermissionGroupResponse)
async def remove_member_from_permission_group(
    group_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove member from permission group (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can remove members from permission groups"
        )

    # Get group
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    # Remove member
    group.members = [m for m in group.members if m.id != user_id]

    await db.commit()
    await db.refresh(group)

    return group


@router.post("/{group_id}/roles", response_model=PermissionGroupResponse)
async def add_roles_to_permission_group(
    group_id: UUID,
    data: PermissionGroupAddRoles,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add roles to permission group (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add roles to permission groups"
        )

    # Get group
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    # Get roles to add
    roles_result = await db.execute(
        select(Role).where(
            and_(
                Role.id.in_(data.role_ids),
                Role.tenant_id == current_user.tenant_id,
                Role.is_deleted == False
            )
        )
    )
    roles = roles_result.scalars().all()

    # Add new roles (avoiding duplicates)
    existing_ids = {r.id for r in group.roles}
    for role in roles:
        if role.id not in existing_ids:
            group.roles.append(role)

    await db.commit()
    await db.refresh(group)

    return group


@router.delete("/{group_id}/roles/{role_id}", response_model=PermissionGroupResponse)
async def remove_role_from_permission_group(
    group_id: UUID,
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove role from permission group (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can remove roles from permission groups"
        )

    # Get group
    result = await db.execute(
        select(PermissionGroup)
        .options(selectinload(PermissionGroup.members))
        .options(selectinload(PermissionGroup.roles))
        .where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    # Remove role
    group.roles = [r for r in group.roles if r.id != role_id]

    await db.commit()
    await db.refresh(group)

    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete permission group (soft delete, admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete permission groups"
        )

    # Get group
    result = await db.execute(
        select(PermissionGroup).where(
            and_(
                PermissionGroup.id == group_id,
                PermissionGroup.tenant_id == current_user.tenant_id,
                PermissionGroup.is_deleted == False
            )
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission group not found"
        )

    # Soft delete
    group.is_deleted = True
    await db.commit()

    return None
