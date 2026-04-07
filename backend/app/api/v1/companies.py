"""Company management endpoints"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.company import Company
from app.schemas.company import CompanyResponse, CompanyUpdate, CompanyCreate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new company (admin only)"""

    company = Company(
        tenant_id=current_user.tenant_id,
        name=company_data.name,
        legal_name=company_data.legal_name,
        company_code=company_data.company_code,
        company_type=company_data.company_type,
        parent_company_id=company_data.parent_company_id,
        primary_email=company_data.primary_email,
        primary_phone=company_data.primary_phone,
        website=company_data.website,
        address_line1=company_data.address_line1,
        city=company_data.city,
        country=company_data.country,
        industry=company_data.industry,
        is_main_it_company=company_data.is_main_it_company,
        status=company_data.status or "active",
    )

    db.add(company)
    await db.commit()
    await db.refresh(company)

    return company


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    company_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all companies"""

    query = select(Company).where(
        Company.tenant_id == current_user.tenant_id,
        Company.is_deleted == False
    )

    if company_type:
        query = query.where(Company.company_type == company_type)

    query = query.order_by(Company.name).offset(skip).limit(limit)

    result = await db.execute(query)
    companies = result.scalars().all()

    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single company"""

    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.tenant_id == current_user.tenant_id,
            Company.is_deleted == False
        )
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_update: CompanyUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a company (admin only)"""

    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.tenant_id == current_user.tenant_id,
            Company.is_deleted == False
        )
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Update fields
    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a company (admin only)"""

    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.tenant_id == current_user.tenant_id,
            Company.is_deleted == False
        )
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Soft delete
    company.is_deleted = True

    await db.commit()

    return None
