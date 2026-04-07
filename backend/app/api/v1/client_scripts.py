"""Client Scripts — Admin CRUD API + public /applicable endpoint"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user, get_current_user
from app.models.user import User
from app.models.client_script import ClientScript
from app.schemas.client_script import (
    ClientScriptCreate,
    ClientScriptUpdate,
    ClientScriptResponse,
    ClientScriptListResponse,
)

router = APIRouter(prefix="/client-scripts", tags=["client-scripts"])


# ── Public endpoint (any authenticated user) ─────────────────────────────────

@router.get("/applicable", response_model=list[ClientScriptResponse])
async def get_applicable_scripts(
    table_name: str = Query("tasks"),
    sys_class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all active client scripts applicable to a given table/ticket type.
    Used by the frontend form to fetch rules on load."""
    query = (
        select(ClientScript)
        .where(
            ClientScript.tenant_id == current_user.tenant_id,
            ClientScript.table_name == table_name,
            ClientScript.is_active == True,
            ClientScript.is_deleted == False,
            or_(
                ClientScript.sys_class_name == sys_class_name,
                ClientScript.sys_class_name == None,
            ),
        )
        .order_by(ClientScript.execution_order)
    )
    result = await db.execute(query)
    return result.scalars().all()


# ── Admin CRUD ────────────────────────────────────────────────────────────────

@router.post("/", response_model=ClientScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_client_script(
    data: ClientScriptCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new client script rule"""
    script = ClientScript(
        tenant_id=current_user.tenant_id,
        name=data.name,
        description=data.description,
        table_name=data.table_name,
        sys_class_name=data.sys_class_name,
        event=data.event,
        trigger_field=data.trigger_field,
        execution_order=data.execution_order,
        condition_logic=data.condition_logic,
        conditions=[c.model_dump() for c in data.conditions],
        ui_actions=[a.model_dump() for a in data.ui_actions],
        is_active=data.is_active,
    )
    db.add(script)
    await db.commit()

    result = await db.execute(
        select(ClientScript).where(ClientScript.id == script.id)
    )
    return result.scalar_one()


@router.get("/", response_model=ClientScriptListResponse)
async def list_client_scripts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    table_name: Optional[str] = Query(None),
    event: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all client script rules"""
    base = select(ClientScript).where(
        ClientScript.tenant_id == current_user.tenant_id,
        ClientScript.is_deleted == False,
    )

    if table_name:
        base = base.where(ClientScript.table_name == table_name)
    if event:
        base = base.where(ClientScript.event == event)
    if search:
        base = base.where(ClientScript.name.ilike(f"%{search}%"))

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(ClientScript.execution_order, ClientScript.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()

    return ClientScriptListResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/{script_id}", response_model=ClientScriptResponse)
async def get_client_script(
    script_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single client script by ID"""
    result = await db.execute(
        select(ClientScript).where(
            ClientScript.id == script_id,
            ClientScript.tenant_id == current_user.tenant_id,
            ClientScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Client script not found")
    return script


@router.put("/{script_id}", response_model=ClientScriptResponse)
async def update_client_script(
    script_id: UUID,
    data: ClientScriptUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a client script"""
    result = await db.execute(
        select(ClientScript).where(
            ClientScript.id == script_id,
            ClientScript.tenant_id == current_user.tenant_id,
            ClientScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Client script not found")

    update_data = data.model_dump(exclude_unset=True)
    if "conditions" in update_data and update_data["conditions"] is not None:
        update_data["conditions"] = [c.model_dump() if hasattr(c, "model_dump") else c for c in update_data["conditions"]]
    if "ui_actions" in update_data and update_data["ui_actions"] is not None:
        update_data["ui_actions"] = [a.model_dump() if hasattr(a, "model_dump") else a for a in update_data["ui_actions"]]

    for field, value in update_data.items():
        setattr(script, field, value)

    await db.commit()

    result = await db.execute(
        select(ClientScript).where(ClientScript.id == script.id)
    )
    return result.scalar_one()


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_script(
    script_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a client script"""
    result = await db.execute(
        select(ClientScript).where(
            ClientScript.id == script_id,
            ClientScript.tenant_id == current_user.tenant_id,
            ClientScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Client script not found")

    script.is_deleted = True
    script.is_active = False
    await db.commit()


@router.post("/{script_id}/toggle", response_model=ClientScriptResponse)
async def toggle_client_script(
    script_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a client script active/inactive"""
    result = await db.execute(
        select(ClientScript).where(
            ClientScript.id == script_id,
            ClientScript.tenant_id == current_user.tenant_id,
            ClientScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Client script not found")

    script.is_active = not script.is_active
    await db.commit()

    result = await db.execute(
        select(ClientScript).where(ClientScript.id == script.id)
    )
    return result.scalar_one()
