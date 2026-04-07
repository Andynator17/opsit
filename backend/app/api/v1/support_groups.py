"""Support Group management endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.support_group import SupportGroup, group_members
from app.schemas.support_group import (
    SupportGroupCreate,
    SupportGroupUpdate,
    SupportGroupResponse,
    SupportGroupListResponse,
    SupportGroupAddMembers,
    SupportGroupMemberUpdate,
)

router = APIRouter(prefix="/support-groups", tags=["support-groups"])


@router.post("/", response_model=SupportGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_support_group(
    group_data: SupportGroupCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new support group (admin only)"""

    group = SupportGroup(
        tenant_id=current_user.tenant_id,
        name=group_data.name,
        description=group_data.description,
        email=group_data.email,
        group_type=group_data.group_type,
        assignment_method=group_data.assignment_method,
        manager_id=group_data.manager_id,
    )

    db.add(group)
    await db.flush()

    # Add members if provided
    if group_data.member_ids:
        for user_id in group_data.member_ids:
            await db.execute(
                group_members.insert().values(
                    group_id=group.id,
                    user_id=user_id
                )
            )

    await db.commit()
    await db.refresh(group)

    return group


@router.get("/", response_model=SupportGroupListResponse)
async def list_support_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all support groups"""

    query = select(SupportGroup).where(
        SupportGroup.tenant_id == current_user.tenant_id,
        SupportGroup.is_deleted == False
    ).order_by(SupportGroup.name)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Execute query
    result = await db.execute(query)
    groups = result.scalars().all()

    return SupportGroupListResponse(
        total=total,
        groups=groups
    )


@router.get("/{group_id}", response_model=SupportGroupResponse)
async def get_support_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single support group"""

    result = await db.execute(
        select(SupportGroup).where(
            SupportGroup.id == group_id,
            SupportGroup.tenant_id == current_user.tenant_id,
            SupportGroup.is_deleted == False
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support group not found"
        )

    return group


@router.patch("/{group_id}", response_model=SupportGroupResponse)
async def update_support_group(
    group_id: UUID,
    group_update: SupportGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a support group (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update support groups"
        )

    result = await db.execute(
        select(SupportGroup).where(
            SupportGroup.id == group_id,
            SupportGroup.tenant_id == current_user.tenant_id,
            SupportGroup.is_deleted == False
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support group not found"
        )

    # Update fields
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)

    return group


@router.post("/{group_id}/members", response_model=SupportGroupResponse)
async def add_members_to_group(
    group_id: UUID,
    members: SupportGroupAddMembers,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add members to support group (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage group members"
        )

    result = await db.execute(
        select(SupportGroup).where(
            SupportGroup.id == group_id,
            SupportGroup.tenant_id == current_user.tenant_id,
            SupportGroup.is_deleted == False
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support group not found"
        )

    # Add members (skip if already exists)
    from sqlalchemy.dialects.postgresql import insert

    for user_id in members.user_ids:
        stmt = insert(group_members).values(
            group_id=group.id,
            user_id=user_id,
            is_team_lead=False
        ).on_conflict_do_nothing(
            index_elements=['group_id', 'user_id']
        )
        await db.execute(stmt)

    await db.commit()
    await db.refresh(group)

    return group


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_group(
    group_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove member from support group (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage group members"
        )

    await db.execute(
        group_members.delete().where(
            group_members.c.group_id == group_id,
            group_members.c.user_id == user_id
        )
    )

    await db.commit()

    return None


@router.patch("/{group_id}/members/{user_id}", response_model=SupportGroupResponse)
async def update_group_member(
    group_id: UUID,
    user_id: UUID,
    member_update: SupportGroupMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update member details in support group (e.g., set team lead) - Admin only"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage group members"
        )

    # Verify group exists and belongs to tenant
    result = await db.execute(
        select(SupportGroup).where(
            SupportGroup.id == group_id,
            SupportGroup.tenant_id == current_user.tenant_id,
            SupportGroup.is_deleted == False
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support group not found"
        )

    # Update member's is_team_lead flag
    await db.execute(
        group_members.update()
        .where(
            group_members.c.group_id == group_id,
            group_members.c.user_id == user_id
        )
        .values(is_team_lead=member_update.is_team_lead)
    )

    await db.commit()
    await db.refresh(group)

    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_support_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a support group (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete support groups"
        )

    result = await db.execute(
        select(SupportGroup).where(
            SupportGroup.id == group_id,
            SupportGroup.tenant_id == current_user.tenant_id,
            SupportGroup.is_deleted == False
        )
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support group not found"
        )

    # Soft delete
    group.is_deleted = True

    await db.commit()

    return None
