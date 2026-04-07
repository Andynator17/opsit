"""Location management endpoints"""
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
from app.models.location import Location
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
)

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new location (admin only)"""
    loc = Location(
        tenant_id=current_user.tenant_id,
        company_id=data.company_id,
        name=data.name,
        address=data.address,
        city=data.city,
        state=data.state,
        country=data.country,
        postal_code=data.postal_code,
    )
    db.add(loc)
    await db.commit()

    # Re-fetch with relationships for response serialization
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.company))
        .where(Location.id == loc.id, Location.tenant_id == current_user.tenant_id)
    )
    return result.scalar_one()


@router.get("/", response_model=LocationListResponse)
async def list_locations(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all locations"""
    query = (
        select(Location)
        .options(selectinload(Location.company))
        .where(
            Location.tenant_id == current_user.tenant_id,
            Location.is_deleted == False,
        )
    )

    if company_id:
        query = query.where(Location.company_id == company_id)

    query = query.order_by(Location.name)
    result = await db.execute(query)
    locations = result.scalars().all()

    return LocationListResponse(total=len(locations), locations=locations)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single location"""
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.company))
        .where(
            Location.id == location_id,
            Location.tenant_id == current_user.tenant_id,
            Location.is_deleted == False,
        )
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return loc


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    data: LocationUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a location (admin only)"""
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.tenant_id == current_user.tenant_id,
            Location.is_deleted == False,
        )
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(loc, field, value)

    await db.commit()

    # Re-fetch with relationships for response serialization
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.company))
        .where(Location.id == location_id, Location.tenant_id == current_user.tenant_id)
    )
    return result.scalar_one()


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a location (admin only)"""
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.tenant_id == current_user.tenant_id,
            Location.is_deleted == False,
        )
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    loc.is_deleted = True
    loc.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None
