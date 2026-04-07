"""System Metadata endpoints — CRUD for all 9 metadata models + public read endpoints."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.sys_db_object import SysDbObject
from app.models.sys_dictionary import SysDictionary
from app.models.sys_choice import SysChoice
from app.models.sys_ui_view import SysUiView
from app.models.sys_ui_section import SysUiSection
from app.models.sys_ui_element import SysUiElement
from app.models.sys_ui_list import SysUiList
from app.models.sys_relationship import SysRelationship
from app.models.sys_ui_related_list import SysUiRelatedList
from app.schemas.sys_metadata import (
    SysDbObjectCreate, SysDbObjectUpdate, SysDbObjectResponse, SysDbObjectListResponse,
    SysDictionaryCreate, SysDictionaryUpdate, SysDictionaryResponse, SysDictionaryListResponse,
    SysChoiceCreate, SysChoiceUpdate, SysChoiceResponse, SysChoiceListResponse,
    SysUiViewCreate, SysUiViewUpdate, SysUiViewResponse,
    SysUiSectionCreate, SysUiSectionUpdate, SysUiSectionResponse,
    SysUiElementCreate, SysUiElementUpdate, SysUiElementResponse,
    SysUiListCreate, SysUiListUpdate, SysUiListResponse,
    SysRelationshipCreate, SysRelationshipUpdate, SysRelationshipResponse, SysRelationshipListResponse,
    SysUiRelatedListCreate, SysUiRelatedListUpdate, SysUiRelatedListResponse,
    TableMetadataResponse, FormLayoutResponse, FormSectionWithElements, ListLayoutResponse,
)

router = APIRouter(prefix="/sys", tags=["system-metadata"])


# ---------------------------------------------------------------------------
# Helper: tenant-aware filter (global + tenant-specific records)
# ---------------------------------------------------------------------------

def _tenant_filter(model, tenant_id):
    """Return filter conditions for tenant-scoped + global (tenant_id=NULL) records."""
    return [
        or_(model.tenant_id == tenant_id, model.tenant_id == None),
        model.is_deleted == False,
    ]


# ===========================================================================
# 1. SysDbObject — /sys/tables/
# ===========================================================================

@router.post("/tables/", response_model=SysDbObjectResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
    data: SysDbObjectCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a table registry entry (admin only)."""
    obj = SysDbObject(
        tenant_id=current_user.tenant_id,
        name=data.name,
        label=data.label,
        plural_label=data.plural_label,
        super_class=data.super_class,
        display_field=data.display_field,
        number_prefix=data.number_prefix,
        is_extendable=data.is_extendable if data.is_extendable is not None else True,
        module=data.module,
        icon=data.icon,
        description=data.description,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysDbObject).where(SysDbObject.id == obj.id))
    return result.scalar_one()


@router.get("/tables/", response_model=SysDbObjectListResponse)
async def list_tables(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all table registry entries (admin only)."""
    query = select(SysDbObject).where(*_tenant_filter(SysDbObject, current_user.tenant_id))

    if table_name:
        query = query.where(SysDbObject.name.ilike(f"%{table_name}%"))

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    query = query.order_by(SysDbObject.name).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()

    return SysDbObjectListResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/tables/{record_id}", response_model=SysDbObjectResponse)
async def get_table(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single table registry entry (admin only)."""
    result = await db.execute(
        select(SysDbObject).where(
            SysDbObject.id == record_id,
            *_tenant_filter(SysDbObject, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table definition not found")
    return obj


@router.put("/tables/{record_id}", response_model=SysDbObjectResponse)
async def update_table(
    record_id: UUID,
    data: SysDbObjectUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a table registry entry (admin only)."""
    result = await db.execute(
        select(SysDbObject).where(
            SysDbObject.id == record_id,
            *_tenant_filter(SysDbObject, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table definition not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysDbObject).where(SysDbObject.id == record_id))
    return refreshed.scalar_one()


@router.delete("/tables/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a table registry entry (admin only)."""
    result = await db.execute(
        select(SysDbObject).where(
            SysDbObject.id == record_id,
            *_tenant_filter(SysDbObject, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table definition not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 2. SysDictionary — /sys/dictionary/
# ===========================================================================

@router.post("/dictionary/", response_model=SysDictionaryResponse, status_code=status.HTTP_201_CREATED)
async def create_dictionary(
    data: SysDictionaryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a field dictionary entry (admin only)."""
    obj = SysDictionary(
        tenant_id=current_user.tenant_id,
        table_name=data.table_name,
        column_name=data.column_name,
        label=data.label,
        field_type=data.field_type,
        max_length=data.max_length,
        is_mandatory=data.is_mandatory if data.is_mandatory is not None else False,
        is_read_only=data.is_read_only if data.is_read_only is not None else False,
        is_display=data.is_display if data.is_display is not None else False,
        default_value=data.default_value,
        reference_table=data.reference_table,
        reference_display_field=data.reference_display_field,
        hint=data.hint,
        description=data.description,
        sort_order=data.sort_order if data.sort_order is not None else 100,
        sys_class_name=data.sys_class_name,
        is_system=data.is_system if data.is_system is not None else False,
        column_exists=data.column_exists if data.column_exists is not None else True,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysDictionary).where(SysDictionary.id == obj.id))
    return result.scalar_one()


@router.get("/dictionary/", response_model=SysDictionaryListResponse)
async def list_dictionary(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List field dictionary entries (admin only)."""
    query = select(SysDictionary).where(*_tenant_filter(SysDictionary, current_user.tenant_id))

    if table_name:
        query = query.where(SysDictionary.table_name == table_name)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(SysDictionary.table_name, SysDictionary.sort_order).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()

    return SysDictionaryListResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/dictionary/{record_id}", response_model=SysDictionaryResponse)
async def get_dictionary(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single field dictionary entry (admin only)."""
    result = await db.execute(
        select(SysDictionary).where(
            SysDictionary.id == record_id,
            *_tenant_filter(SysDictionary, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictionary entry not found")
    return obj


@router.put("/dictionary/{record_id}", response_model=SysDictionaryResponse)
async def update_dictionary(
    record_id: UUID,
    data: SysDictionaryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a field dictionary entry (admin only)."""
    result = await db.execute(
        select(SysDictionary).where(
            SysDictionary.id == record_id,
            *_tenant_filter(SysDictionary, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictionary entry not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysDictionary).where(SysDictionary.id == record_id))
    return refreshed.scalar_one()


@router.delete("/dictionary/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dictionary(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a field dictionary entry (admin only)."""
    result = await db.execute(
        select(SysDictionary).where(
            SysDictionary.id == record_id,
            *_tenant_filter(SysDictionary, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dictionary entry not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 3. SysChoice — /sys/choices/
# ===========================================================================

@router.post("/choices/", response_model=SysChoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_choice(
    data: SysChoiceCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a choice list entry (admin only)."""
    obj = SysChoice(
        tenant_id=current_user.tenant_id,
        table_name=data.table_name,
        field_name=data.field_name,
        value=data.value,
        label=data.label,
        sequence=data.sequence if data.sequence is not None else 100,
        sys_class_name=data.sys_class_name,
        dependent_field=data.dependent_field,
        dependent_value=data.dependent_value,
        color=data.color,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysChoice).where(SysChoice.id == obj.id))
    return result.scalar_one()


@router.get("/choices/", response_model=SysChoiceListResponse)
async def list_choices(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List choice entries (admin only)."""
    query = select(SysChoice).where(*_tenant_filter(SysChoice, current_user.tenant_id))

    if table_name:
        query = query.where(SysChoice.table_name == table_name)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(SysChoice.table_name, SysChoice.field_name, SysChoice.sequence).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()

    return SysChoiceListResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/choices/{record_id}", response_model=SysChoiceResponse)
async def get_choice(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single choice entry (admin only)."""
    result = await db.execute(
        select(SysChoice).where(
            SysChoice.id == record_id,
            *_tenant_filter(SysChoice, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Choice entry not found")
    return obj


@router.put("/choices/{record_id}", response_model=SysChoiceResponse)
async def update_choice(
    record_id: UUID,
    data: SysChoiceUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a choice entry (admin only)."""
    result = await db.execute(
        select(SysChoice).where(
            SysChoice.id == record_id,
            *_tenant_filter(SysChoice, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Choice entry not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysChoice).where(SysChoice.id == record_id))
    return refreshed.scalar_one()


@router.delete("/choices/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_choice(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a choice entry (admin only)."""
    result = await db.execute(
        select(SysChoice).where(
            SysChoice.id == record_id,
            *_tenant_filter(SysChoice, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Choice entry not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 4. SysUiView — /sys/views/
# ===========================================================================

@router.post("/views/", response_model=SysUiViewResponse, status_code=status.HTTP_201_CREATED)
async def create_view(
    data: SysUiViewCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a UI view definition (admin only)."""
    obj = SysUiView(
        tenant_id=current_user.tenant_id,
        name=data.name,
        title=data.title,
        table_name=data.table_name,
        sys_class_name=data.sys_class_name,
        description=data.description,
        is_default=data.is_default if data.is_default is not None else False,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysUiView).where(SysUiView.id == obj.id))
    return result.scalar_one()


@router.get("/views/", response_model=List[SysUiViewResponse])
async def list_views(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List UI view definitions (admin only)."""
    query = select(SysUiView).where(*_tenant_filter(SysUiView, current_user.tenant_id))

    if table_name:
        query = query.where(SysUiView.table_name == table_name)

    query = query.order_by(SysUiView.table_name, SysUiView.name).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return items


@router.get("/views/{record_id}", response_model=SysUiViewResponse)
async def get_view(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single UI view definition (admin only)."""
    result = await db.execute(
        select(SysUiView).where(
            SysUiView.id == record_id,
            *_tenant_filter(SysUiView, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="View not found")
    return obj


@router.put("/views/{record_id}", response_model=SysUiViewResponse)
async def update_view(
    record_id: UUID,
    data: SysUiViewUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a UI view definition (admin only)."""
    result = await db.execute(
        select(SysUiView).where(
            SysUiView.id == record_id,
            *_tenant_filter(SysUiView, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="View not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysUiView).where(SysUiView.id == record_id))
    return refreshed.scalar_one()


@router.delete("/views/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_view(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a UI view definition (admin only)."""
    result = await db.execute(
        select(SysUiView).where(
            SysUiView.id == record_id,
            *_tenant_filter(SysUiView, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="View not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 5. SysUiSection — /sys/sections/
# ===========================================================================

@router.post("/sections/", response_model=SysUiSectionResponse, status_code=status.HTTP_201_CREATED)
async def create_section(
    data: SysUiSectionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a form section (admin only)."""
    obj = SysUiSection(
        tenant_id=current_user.tenant_id,
        view_id=data.view_id,
        title=data.title,
        section_type=data.section_type or "fields",
        columns=data.columns if data.columns is not None else 2,
        sequence=data.sequence if data.sequence is not None else 100,
        is_expanded=data.is_expanded if data.is_expanded is not None else True,
        position=data.position or "full",
        sys_class_name=data.sys_class_name,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysUiSection).where(SysUiSection.id == obj.id))
    return result.scalar_one()


@router.get("/sections/", response_model=List[SysUiSectionResponse])
async def list_sections(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    table_name: Optional[str] = Query(None, description="Filter by table name (requires view lookup)"),
    view_id: Optional[UUID] = Query(None, description="Filter by view ID"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List form sections (admin only)."""
    query = select(SysUiSection).where(*_tenant_filter(SysUiSection, current_user.tenant_id))

    if view_id:
        query = query.where(SysUiSection.view_id == view_id)

    if table_name and not view_id:
        # Look up view IDs for table_name first
        view_subq = select(SysUiView.id).where(
            SysUiView.table_name == table_name,
            *_tenant_filter(SysUiView, current_user.tenant_id),
        ).subquery()
        query = query.where(SysUiSection.view_id.in_(select(view_subq)))

    query = query.order_by(SysUiSection.sequence).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return items


@router.get("/sections/{record_id}", response_model=SysUiSectionResponse)
async def get_section(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single form section (admin only)."""
    result = await db.execute(
        select(SysUiSection).where(
            SysUiSection.id == record_id,
            *_tenant_filter(SysUiSection, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return obj


@router.put("/sections/{record_id}", response_model=SysUiSectionResponse)
async def update_section(
    record_id: UUID,
    data: SysUiSectionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a form section (admin only)."""
    result = await db.execute(
        select(SysUiSection).where(
            SysUiSection.id == record_id,
            *_tenant_filter(SysUiSection, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysUiSection).where(SysUiSection.id == record_id))
    return refreshed.scalar_one()


@router.delete("/sections/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a form section (admin only)."""
    result = await db.execute(
        select(SysUiSection).where(
            SysUiSection.id == record_id,
            *_tenant_filter(SysUiSection, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 6. SysUiElement — /sys/elements/
# ===========================================================================

@router.post("/elements/", response_model=SysUiElementResponse, status_code=status.HTTP_201_CREATED)
async def create_element(
    data: SysUiElementCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a form element (admin only)."""
    obj = SysUiElement(
        tenant_id=current_user.tenant_id,
        section_id=data.section_id,
        field_name=data.field_name,
        element_type=data.element_type or "field",
        sequence=data.sequence if data.sequence is not None else 100,
        column_index=data.column_index if data.column_index is not None else 1,
        annotation_text=data.annotation_text,
        span=data.span if data.span is not None else 1,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysUiElement).where(SysUiElement.id == obj.id))
    return result.scalar_one()


@router.get("/elements/", response_model=List[SysUiElementResponse])
async def list_elements(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    section_id: Optional[UUID] = Query(None, description="Filter by section ID"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List form elements (admin only)."""
    query = select(SysUiElement).where(*_tenant_filter(SysUiElement, current_user.tenant_id))

    if section_id:
        query = query.where(SysUiElement.section_id == section_id)

    query = query.order_by(SysUiElement.sequence).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return items


@router.get("/elements/{record_id}", response_model=SysUiElementResponse)
async def get_element(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single form element (admin only)."""
    result = await db.execute(
        select(SysUiElement).where(
            SysUiElement.id == record_id,
            *_tenant_filter(SysUiElement, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Element not found")
    return obj


@router.put("/elements/{record_id}", response_model=SysUiElementResponse)
async def update_element(
    record_id: UUID,
    data: SysUiElementUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a form element (admin only)."""
    result = await db.execute(
        select(SysUiElement).where(
            SysUiElement.id == record_id,
            *_tenant_filter(SysUiElement, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Element not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysUiElement).where(SysUiElement.id == record_id))
    return refreshed.scalar_one()


@router.delete("/elements/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_element(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a form element (admin only)."""
    result = await db.execute(
        select(SysUiElement).where(
            SysUiElement.id == record_id,
            *_tenant_filter(SysUiElement, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Element not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 7. SysUiList — /sys/list-columns/
# ===========================================================================

@router.post("/list-columns/", response_model=SysUiListResponse, status_code=status.HTTP_201_CREATED)
async def create_list_column(
    data: SysUiListCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a list column entry (admin only)."""
    obj = SysUiList(
        tenant_id=current_user.tenant_id,
        view_id=data.view_id,
        field_name=data.field_name,
        sequence=data.sequence if data.sequence is not None else 100,
        sort_direction=data.sort_direction,
        sort_priority=data.sort_priority,
        width=data.width,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysUiList).where(SysUiList.id == obj.id))
    return result.scalar_one()


@router.get("/list-columns/", response_model=List[SysUiListResponse])
async def list_list_columns(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    view_id: Optional[UUID] = Query(None, description="Filter by view ID"),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List list-column entries (admin only)."""
    query = select(SysUiList).where(*_tenant_filter(SysUiList, current_user.tenant_id))

    if view_id:
        query = query.where(SysUiList.view_id == view_id)

    if table_name and not view_id:
        view_subq = select(SysUiView.id).where(
            SysUiView.table_name == table_name,
            *_tenant_filter(SysUiView, current_user.tenant_id),
        ).subquery()
        query = query.where(SysUiList.view_id.in_(select(view_subq)))

    query = query.order_by(SysUiList.sequence).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return items


@router.get("/list-columns/{record_id}", response_model=SysUiListResponse)
async def get_list_column(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single list column entry (admin only)."""
    result = await db.execute(
        select(SysUiList).where(
            SysUiList.id == record_id,
            *_tenant_filter(SysUiList, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List column not found")
    return obj


@router.put("/list-columns/{record_id}", response_model=SysUiListResponse)
async def update_list_column(
    record_id: UUID,
    data: SysUiListUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a list column entry (admin only)."""
    result = await db.execute(
        select(SysUiList).where(
            SysUiList.id == record_id,
            *_tenant_filter(SysUiList, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List column not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysUiList).where(SysUiList.id == record_id))
    return refreshed.scalar_one()


@router.delete("/list-columns/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_column(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a list column entry (admin only)."""
    result = await db.execute(
        select(SysUiList).where(
            SysUiList.id == record_id,
            *_tenant_filter(SysUiList, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List column not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 8. SysRelationship — /sys/relationships/
# ===========================================================================

@router.post("/relationships/", response_model=SysRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    data: SysRelationshipCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a table relationship (admin only)."""
    obj = SysRelationship(
        tenant_id=current_user.tenant_id,
        name=data.name,
        parent_table=data.parent_table,
        child_table=data.child_table,
        relationship_type=data.relationship_type,
        foreign_key_field=data.foreign_key_field,
        join_table=data.join_table,
        join_parent_field=data.join_parent_field,
        join_child_field=data.join_child_field,
        description=data.description,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysRelationship).where(SysRelationship.id == obj.id))
    return result.scalar_one()


@router.get("/relationships/", response_model=SysRelationshipListResponse)
async def list_relationships(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    table_name: Optional[str] = Query(None, description="Filter by parent table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List table relationships (admin only)."""
    query = select(SysRelationship).where(*_tenant_filter(SysRelationship, current_user.tenant_id))

    if table_name:
        query = query.where(SysRelationship.parent_table == table_name)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(SysRelationship.parent_table, SysRelationship.name).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()

    return SysRelationshipListResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/relationships/{record_id}", response_model=SysRelationshipResponse)
async def get_relationship(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single table relationship (admin only)."""
    result = await db.execute(
        select(SysRelationship).where(
            SysRelationship.id == record_id,
            *_tenant_filter(SysRelationship, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    return obj


@router.put("/relationships/{record_id}", response_model=SysRelationshipResponse)
async def update_relationship(
    record_id: UUID,
    data: SysRelationshipUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a table relationship (admin only)."""
    result = await db.execute(
        select(SysRelationship).where(
            SysRelationship.id == record_id,
            *_tenant_filter(SysRelationship, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysRelationship).where(SysRelationship.id == record_id))
    return refreshed.scalar_one()


@router.delete("/relationships/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a table relationship (admin only)."""
    result = await db.execute(
        select(SysRelationship).where(
            SysRelationship.id == record_id,
            *_tenant_filter(SysRelationship, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# 9. SysUiRelatedList — /sys/related-lists/
# ===========================================================================

@router.post("/related-lists/", response_model=SysUiRelatedListResponse, status_code=status.HTTP_201_CREATED)
async def create_related_list(
    data: SysUiRelatedListCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a related list entry (admin only)."""
    obj = SysUiRelatedList(
        tenant_id=current_user.tenant_id,
        view_id=data.view_id,
        relationship_id=data.relationship_id,
        title=data.title,
        sequence=data.sequence if data.sequence is not None else 100,
        display_fields=data.display_fields or [],
        filter_condition=data.filter_condition,
        max_rows=data.max_rows if data.max_rows is not None else 20,
        sys_class_name=data.sys_class_name,
    )
    db.add(obj)
    await db.commit()

    result = await db.execute(select(SysUiRelatedList).where(SysUiRelatedList.id == obj.id))
    return result.scalar_one()


@router.get("/related-lists/", response_model=List[SysUiRelatedListResponse])
async def list_related_lists(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    view_id: Optional[UUID] = Query(None, description="Filter by view ID"),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List related list entries (admin only)."""
    query = select(SysUiRelatedList).where(*_tenant_filter(SysUiRelatedList, current_user.tenant_id))

    if view_id:
        query = query.where(SysUiRelatedList.view_id == view_id)

    if table_name and not view_id:
        view_subq = select(SysUiView.id).where(
            SysUiView.table_name == table_name,
            *_tenant_filter(SysUiView, current_user.tenant_id),
        ).subquery()
        query = query.where(SysUiRelatedList.view_id.in_(select(view_subq)))

    query = query.order_by(SysUiRelatedList.sequence).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return items


@router.get("/related-lists/{record_id}", response_model=SysUiRelatedListResponse)
async def get_related_list(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single related list entry (admin only)."""
    result = await db.execute(
        select(SysUiRelatedList).where(
            SysUiRelatedList.id == record_id,
            *_tenant_filter(SysUiRelatedList, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related list not found")
    return obj


@router.put("/related-lists/{record_id}", response_model=SysUiRelatedListResponse)
async def update_related_list(
    record_id: UUID,
    data: SysUiRelatedListUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a related list entry (admin only)."""
    result = await db.execute(
        select(SysUiRelatedList).where(
            SysUiRelatedList.id == record_id,
            *_tenant_filter(SysUiRelatedList, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related list not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()

    refreshed = await db.execute(select(SysUiRelatedList).where(SysUiRelatedList.id == record_id))
    return refreshed.scalar_one()


@router.delete("/related-lists/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_related_list(
    record_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a related list entry (admin only)."""
    result = await db.execute(
        select(SysUiRelatedList).where(
            SysUiRelatedList.id == record_id,
            *_tenant_filter(SysUiRelatedList, current_user.tenant_id),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related list not found")

    obj.is_deleted = True
    obj.is_active = False
    obj.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return None


# ===========================================================================
# PUBLIC ENDPOINTS — any authenticated user
# ===========================================================================

@router.get("/metadata/{table_name}", response_model=TableMetadataResponse)
async def get_table_metadata(
    table_name: str,
    sys_class_name: Optional[str] = Query(None, description="Filter fields/choices by sys_class_name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return table info + dictionary fields + choices + relationships for a table.
    Includes inherited fields from super_class chain.
    """
    tenant_filter = _tenant_filter

    # 1. Fetch SysDbObject
    result = await db.execute(
        select(SysDbObject).where(
            SysDbObject.name == table_name,
            *tenant_filter(SysDbObject, current_user.tenant_id),
        )
    )
    table_obj = result.scalar_one_or_none()
    if not table_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Table '{table_name}' not found")

    # 2. Collect table names to query (include inherited from super_class chain)
    table_names = [table_name]
    visited = {table_name}
    current_super = table_obj.super_class
    while current_super and current_super not in visited:
        table_names.append(current_super)
        visited.add(current_super)
        # Look up next super_class
        parent_result = await db.execute(
            select(SysDbObject.super_class).where(
                SysDbObject.name == current_super,
                *tenant_filter(SysDbObject, current_user.tenant_id),
            )
        )
        row = parent_result.scalar_one_or_none()
        current_super = row if row else None

    # 3. Fetch SysDictionary for all tables in the inheritance chain
    dict_query = select(SysDictionary).where(
        SysDictionary.table_name.in_(table_names),
        *tenant_filter(SysDictionary, current_user.tenant_id),
    )
    if sys_class_name:
        dict_query = dict_query.where(
            or_(
                SysDictionary.sys_class_name == sys_class_name,
                SysDictionary.sys_class_name == None,
            )
        )
    dict_query = dict_query.order_by(SysDictionary.sort_order)
    dict_result = await db.execute(dict_query)
    fields = dict_result.scalars().all()

    # 4. Fetch SysChoice for all tables in the inheritance chain
    choice_query = select(SysChoice).where(
        SysChoice.table_name.in_(table_names),
        *tenant_filter(SysChoice, current_user.tenant_id),
    )
    if sys_class_name:
        choice_query = choice_query.where(
            or_(
                SysChoice.sys_class_name == sys_class_name,
                SysChoice.sys_class_name == None,
            )
        )
    choice_query = choice_query.order_by(SysChoice.sequence)
    choice_result = await db.execute(choice_query)
    choices = choice_result.scalars().all()

    # 5. Fetch SysRelationship where parent_table matches
    rel_query = select(SysRelationship).where(
        SysRelationship.parent_table.in_(table_names),
        *tenant_filter(SysRelationship, current_user.tenant_id),
    )
    rel_result = await db.execute(rel_query)
    relationships = rel_result.scalars().all()

    return TableMetadataResponse(
        table=table_obj,
        fields=fields,
        choices=choices,
        relationships=relationships,
    )


@router.get("/form-layout/{table_name}", response_model=FormLayoutResponse)
async def get_form_layout(
    table_name: str,
    view_name: str = Query("default", description="View name"),
    sys_class_name: Optional[str] = Query(None, description="Filter by sys_class_name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return view + sections (with nested elements) + related lists for a form.
    Falls back to NULL sys_class_name if specific one not found.
    """
    tenant_conds = _tenant_filter

    # 1. Find SysUiView — try exact sys_class_name first, then fall back to NULL
    view = None
    if sys_class_name:
        result = await db.execute(
            select(SysUiView).where(
                SysUiView.table_name == table_name,
                SysUiView.name == view_name,
                SysUiView.sys_class_name == sys_class_name,
                *tenant_conds(SysUiView, current_user.tenant_id),
            )
        )
        view = result.scalar_one_or_none()

    if not view:
        # Fall back to NULL sys_class_name (generic view)
        result = await db.execute(
            select(SysUiView).where(
                SysUiView.table_name == table_name,
                SysUiView.name == view_name,
                SysUiView.sys_class_name == None,
                *tenant_conds(SysUiView, current_user.tenant_id),
            )
        )
        view = result.scalar_one_or_none()

    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"View '{view_name}' not found for table '{table_name}'",
        )

    # 2. Fetch sections for this view, ordered by sequence
    section_query = select(SysUiSection).where(
        SysUiSection.view_id == view.id,
        *tenant_conds(SysUiSection, current_user.tenant_id),
    )
    if sys_class_name:
        section_query = section_query.where(
            or_(
                SysUiSection.sys_class_name == sys_class_name,
                SysUiSection.sys_class_name == None,
            )
        )
    section_query = section_query.order_by(SysUiSection.sequence)
    section_result = await db.execute(section_query)
    sections = section_result.scalars().all()

    # 3. For each section, fetch elements ordered by sequence
    sections_with_elements = []
    for section in sections:
        elem_result = await db.execute(
            select(SysUiElement).where(
                SysUiElement.section_id == section.id,
                *tenant_conds(SysUiElement, current_user.tenant_id),
            ).order_by(SysUiElement.sequence)
        )
        elements = elem_result.scalars().all()
        sections_with_elements.append(
            FormSectionWithElements(
                id=section.id,
                title=section.title,
                section_type=section.section_type,
                columns=section.columns,
                sequence=section.sequence,
                is_expanded=section.is_expanded,
                position=section.position,
                sys_class_name=section.sys_class_name,
                elements=elements,
            )
        )

    # 4. Fetch related lists for this view
    rl_query = select(SysUiRelatedList).where(
        SysUiRelatedList.view_id == view.id,
        *tenant_conds(SysUiRelatedList, current_user.tenant_id),
    )
    if sys_class_name:
        rl_query = rl_query.where(
            or_(
                SysUiRelatedList.sys_class_name == sys_class_name,
                SysUiRelatedList.sys_class_name == None,
            )
        )
    rl_query = rl_query.order_by(SysUiRelatedList.sequence)
    rl_result = await db.execute(rl_query)
    related_lists = rl_result.scalars().all()

    return FormLayoutResponse(
        view=view,
        sections=sections_with_elements,
        related_lists=related_lists,
    )


@router.get("/list-layout/{table_name}", response_model=ListLayoutResponse)
async def get_list_layout(
    table_name: str,
    view_name: str = Query("default", description="View name"),
    sys_class_name: Optional[str] = Query(None, description="Filter by sys_class_name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return view + list columns for a table's list layout.
    Falls back to NULL sys_class_name if specific one not found.
    """
    tenant_conds = _tenant_filter

    # 1. Find SysUiView — try exact sys_class_name first, then fall back to NULL
    view = None
    if sys_class_name:
        result = await db.execute(
            select(SysUiView).where(
                SysUiView.table_name == table_name,
                SysUiView.name == view_name,
                SysUiView.sys_class_name == sys_class_name,
                *tenant_conds(SysUiView, current_user.tenant_id),
            )
        )
        view = result.scalar_one_or_none()

    if not view:
        result = await db.execute(
            select(SysUiView).where(
                SysUiView.table_name == table_name,
                SysUiView.name == view_name,
                SysUiView.sys_class_name == None,
                *tenant_conds(SysUiView, current_user.tenant_id),
            )
        )
        view = result.scalar_one_or_none()

    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"View '{view_name}' not found for table '{table_name}'",
        )

    # 2. Fetch SysUiList entries ordered by sequence
    list_result = await db.execute(
        select(SysUiList).where(
            SysUiList.view_id == view.id,
            *tenant_conds(SysUiList, current_user.tenant_id),
        ).order_by(SysUiList.sequence)
    )
    columns = list_result.scalars().all()

    return ListLayoutResponse(
        view=view,
        columns=columns,
    )
