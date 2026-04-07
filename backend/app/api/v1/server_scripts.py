"""Server Scripts (Business Rules) — Admin CRUD API"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.server_script import ServerScript
from app.schemas.server_script import (
    ServerScriptCreate,
    ServerScriptUpdate,
    ServerScriptResponse,
    ServerScriptListResponse,
)

router = APIRouter(prefix="/server-scripts", tags=["server-scripts"])


@router.post("/", response_model=ServerScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_server_script(
    data: ServerScriptCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new server script rule"""
    script = ServerScript(
        tenant_id=current_user.tenant_id,
        name=data.name,
        description=data.description,
        table_name=data.table_name,
        sys_class_name=data.sys_class_name,
        timing=data.timing,
        execution_order=data.execution_order,
        condition_logic=data.condition_logic,
        conditions=[c.model_dump() for c in data.conditions],
        actions=[a.model_dump() for a in data.actions],
        is_active=data.is_active,
    )
    db.add(script)
    await db.commit()

    result = await db.execute(
        select(ServerScript).where(ServerScript.id == script.id)
    )
    return result.scalar_one()


@router.get("/", response_model=ServerScriptListResponse)
async def list_server_scripts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    table_name: Optional[str] = Query(None),
    timing: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all server script rules"""
    base = select(ServerScript).where(
        ServerScript.tenant_id == current_user.tenant_id,
        ServerScript.is_deleted == False,
    )

    if table_name:
        base = base.where(ServerScript.table_name == table_name)
    if timing:
        base = base.where(ServerScript.timing == timing)
    if search:
        base = base.where(ServerScript.name.ilike(f"%{search}%"))

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(ServerScript.execution_order, ServerScript.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()

    return ServerScriptListResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/{script_id}", response_model=ServerScriptResponse)
async def get_server_script(
    script_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single server script by ID"""
    result = await db.execute(
        select(ServerScript).where(
            ServerScript.id == script_id,
            ServerScript.tenant_id == current_user.tenant_id,
            ServerScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Server script not found")
    return script


@router.put("/{script_id}", response_model=ServerScriptResponse)
async def update_server_script(
    script_id: UUID,
    data: ServerScriptUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a server script"""
    result = await db.execute(
        select(ServerScript).where(
            ServerScript.id == script_id,
            ServerScript.tenant_id == current_user.tenant_id,
            ServerScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Server script not found")

    update_data = data.model_dump(exclude_unset=True)
    # Serialize pydantic models in conditions/actions to dicts
    if "conditions" in update_data and update_data["conditions"] is not None:
        update_data["conditions"] = [c.model_dump() if hasattr(c, "model_dump") else c for c in update_data["conditions"]]
    if "actions" in update_data and update_data["actions"] is not None:
        update_data["actions"] = [a.model_dump() if hasattr(a, "model_dump") else a for a in update_data["actions"]]

    for field, value in update_data.items():
        setattr(script, field, value)

    await db.commit()

    result = await db.execute(
        select(ServerScript).where(ServerScript.id == script.id)
    )
    return result.scalar_one()


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server_script(
    script_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a server script"""
    result = await db.execute(
        select(ServerScript).where(
            ServerScript.id == script_id,
            ServerScript.tenant_id == current_user.tenant_id,
            ServerScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Server script not found")

    script.is_deleted = True
    script.is_active = False
    await db.commit()


@router.post("/{script_id}/toggle", response_model=ServerScriptResponse)
async def toggle_server_script(
    script_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a server script active/inactive"""
    result = await db.execute(
        select(ServerScript).where(
            ServerScript.id == script_id,
            ServerScript.tenant_id == current_user.tenant_id,
            ServerScript.is_deleted == False,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Server script not found")

    script.is_active = not script.is_active
    await db.commit()

    result = await db.execute(
        select(ServerScript).where(ServerScript.id == script.id)
    )
    return result.scalar_one()
