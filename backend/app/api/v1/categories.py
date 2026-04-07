"""Category management endpoints"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category (admin only)"""

    category = Category(
        tenant_id=current_user.tenant_id,
        name=category_data.name,
        description=category_data.description,
        category_type=category_data.category_type,
        parent_category_id=category_data.parent_category_id,
        level=category_data.level,
        sort_order=category_data.sort_order,
        icon=category_data.icon,
        color=category_data.color,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    category_type: Optional[str] = Query(None, description="Filter by type"),
    level: Optional[int] = Query(None, description="Filter by level"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all categories"""

    query = select(Category).where(
        Category.tenant_id == current_user.tenant_id,
        Category.is_deleted == False
    )

    if category_type:
        query = query.where(Category.category_type == category_type)

    if level:
        query = query.where(Category.level == level)

    if parent_id:
        query = query.where(Category.parent_category_id == parent_id)

    # Order by sort_order, then name
    query = query.order_by(Category.sort_order, Category.name)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Execute query
    result = await db.execute(query)
    categories = result.scalars().all()

    return CategoryListResponse(
        total=total,
        categories=categories
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single category"""

    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.tenant_id == current_user.tenant_id,
            Category.is_deleted == False
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a category (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update categories"
        )

    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.tenant_id == current_user.tenant_id,
            Category.is_deleted == False
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Update fields
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a category (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete categories"
        )

    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.tenant_id == current_user.tenant_id,
            Category.is_deleted == False
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Soft delete
    category.is_deleted = True

    await db.commit()

    return None
