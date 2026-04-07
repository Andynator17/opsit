"""Portal management endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.portal import Portal
from app.schemas.portal import (
    PortalResponse, PortalCreate, PortalUpdate,
    PortalPublicResponse, PortalListResponse,
)

router = APIRouter(prefix="/portals", tags=["portals"])


# --- Admin CRUD ---

@router.post("/", response_model=PortalResponse, status_code=status.HTTP_201_CREATED)
async def create_portal(
    data: PortalCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new portal (admin only)"""
    # Check slug uniqueness
    existing = await db.execute(
        select(Portal).where(Portal.slug == data.slug, Portal.is_deleted == False)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Portal slug already exists")

    portal = Portal(
        tenant_id=current_user.tenant_id,
        **data.model_dump(),
    )
    db.add(portal)
    await db.commit()

    result = await db.execute(select(Portal).where(Portal.id == portal.id))
    return result.scalar_one()


@router.get("/", response_model=PortalListResponse)
async def list_portals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all portals (admin only)"""
    base = select(Portal).where(
        Portal.tenant_id == current_user.tenant_id,
        Portal.is_deleted == False,
    )

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(Portal.sort_order, Portal.name).offset(skip).limit(limit)
    )
    items = result.scalars().all()

    return PortalListResponse(items=items, total=total)


@router.put("/{portal_id}", response_model=PortalResponse)
async def update_portal(
    portal_id: UUID,
    data: PortalUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a portal (admin only)"""
    result = await db.execute(
        select(Portal).where(
            Portal.id == portal_id,
            Portal.tenant_id == current_user.tenant_id,
            Portal.is_deleted == False,
        )
    )
    portal = result.scalar_one_or_none()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")

    update_data = data.model_dump(exclude_unset=True)

    # Check slug uniqueness if changing
    if "slug" in update_data and update_data["slug"] != portal.slug:
        existing = await db.execute(
            select(Portal).where(
                Portal.slug == update_data["slug"],
                Portal.is_deleted == False,
                Portal.id != portal_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Portal slug already exists")

    for field, value in update_data.items():
        setattr(portal, field, value)

    await db.commit()

    result = await db.execute(select(Portal).where(Portal.id == portal_id))
    return result.scalar_one()


@router.delete("/{portal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portal(
    portal_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a portal (admin only)"""
    result = await db.execute(
        select(Portal).where(
            Portal.id == portal_id,
            Portal.tenant_id == current_user.tenant_id,
            Portal.is_deleted == False,
        )
    )
    portal = result.scalar_one_or_none()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")

    portal.is_deleted = True
    await db.commit()
    return None


# --- End-user endpoints ---

@router.get("/my", response_model=List[PortalPublicResponse])
async def get_my_portals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get portals accessible to the current user"""
    query = select(Portal).where(
        Portal.tenant_id == current_user.tenant_id,
        Portal.is_deleted == False,
        Portal.is_active == True,
    )

    # Filter by audience: internal portals + company-specific portals for user's company
    from sqlalchemy import or_
    query = query.where(
        or_(
            Portal.audience_type == "internal",
            (Portal.audience_type == "company") & (Portal.company_id == current_user.primary_company_id),
        )
    )

    result = await db.execute(query.order_by(Portal.sort_order, Portal.name))
    return result.scalars().all()


@router.get("/by-slug/{slug}", response_model=PortalPublicResponse)
async def get_portal_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get portal config by slug (for branding)"""
    result = await db.execute(
        select(Portal).where(
            Portal.slug == slug,
            Portal.tenant_id == current_user.tenant_id,
            Portal.is_deleted == False,
            Portal.is_active == True,
        )
    )
    portal = result.scalar_one_or_none()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")

    # Check audience access
    if portal.audience_type == "company" and portal.company_id != current_user.primary_company_id:
        raise HTTPException(status_code=403, detail="Access denied to this portal")

    return portal
