"""User management endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information"""

    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users in the tenant"""

    result = await db.execute(
        select(User)
        .where(
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin only)"""

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin only)"""

    # Check if email already exists
    result = await db.execute(
        select(User).where(
            User.email == user_data.email,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate user_id from email if not provided
    user_id = user_data.email.split('@')[0]

    # Check if user_id already exists
    result = await db.execute(
        select(User).where(
            User.user_id == user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
    )
    if result.scalar_one_or_none():
        # Append a number to make it unique
        count = 1
        while True:
            test_user_id = f"{user_id}{count}"
            result = await db.execute(
                select(User).where(
                    User.user_id == test_user_id,
                    User.tenant_id == current_user.tenant_id,
                    User.is_deleted == False
                )
            )
            if not result.scalar_one_or_none():
                user_id = test_user_id
                break
            count += 1

    # Compute full name if not provided
    full_name = user_data.full_name
    if not full_name:
        parts = []
        if user_data.salutation:
            parts.append(user_data.salutation)
        if user_data.title:
            parts.append(user_data.title)
        parts.append(user_data.first_name)
        if user_data.middle_name:
            parts.append(user_data.middle_name)
        parts.append(user_data.last_name)
        full_name = " ".join(parts)

    # Create new user
    new_user = User(
        tenant_id=current_user.tenant_id,
        primary_company_id=user_data.company_id or current_user.primary_company_id,
        user_id=user_id,
        email=user_data.email,
        email_secondary=user_data.email_secondary,
        password_hash=get_password_hash(user_data.password),
        employee_id=user_data.employee_id,
        salutation=user_data.salutation,
        title=user_data.title,
        first_name=user_data.first_name,
        middle_name=user_data.middle_name,
        last_name=user_data.last_name,
        full_name=full_name,
        gender=user_data.gender,
        phone=user_data.phone,
        phone_secondary=user_data.phone_secondary,
        mobile=user_data.mobile,
        job_title=user_data.job_title,
        department=user_data.department,
        location=user_data.location,
        user_type=user_data.user_type,
        language=user_data.language,
        timezone=user_data.timezone,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)"""

    # Get user
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)

    # Compute full name if name fields changed
    if any(k in update_data for k in ['salutation', 'title', 'first_name', 'middle_name', 'last_name']):
        parts = []
        if update_data.get('salutation') or user.salutation:
            parts.append(update_data.get('salutation', user.salutation))
        if update_data.get('title') or user.title:
            parts.append(update_data.get('title', user.title))
        parts.append(update_data.get('first_name', user.first_name))
        if update_data.get('middle_name') or user.middle_name:
            parts.append(update_data.get('middle_name', user.middle_name))
        parts.append(update_data.get('last_name', user.last_name))
        update_data['full_name'] = " ".join(parts)

    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete user (admin only)"""

    # Get user
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete
    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)

    await db.commit()

    return None
