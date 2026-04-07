"""Seed default RBAC roles"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role
from app.core.permissions import Permissions


# Define default roles for each module with 4 levels
DEFAULT_ROLES = [
    # Incident Module
    {
        "name": "Incident Read",
        "code": "incident_read",
        "description": "Can view incidents",
        "module": "incident",
        "level": "read",
        "permissions": [Permissions.INCIDENT_READ],
        "is_system_role": True
    },
    {
        "name": "Incident Read & Create",
        "code": "incident_read_create",
        "description": "Can view and create incidents",
        "module": "incident",
        "level": "read_create",
        "permissions": [Permissions.INCIDENT_READ, Permissions.INCIDENT_CREATE],
        "is_system_role": True
    },
    {
        "name": "Incident Agent",
        "code": "incident_agent",
        "description": "Can view, create, update, assign, and resolve incidents",
        "module": "incident",
        "level": "agent",
        "permissions": [
            Permissions.INCIDENT_READ,
            Permissions.INCIDENT_CREATE,
            Permissions.INCIDENT_UPDATE,
            Permissions.INCIDENT_ASSIGN,
            Permissions.INCIDENT_RESOLVE
        ],
        "is_system_role": True
    },
    {
        "name": "Incident Admin",
        "code": "incident_admin",
        "description": "Full control over incidents",
        "module": "incident",
        "level": "admin",
        "permissions": [Permissions.INCIDENT_ADMIN],
        "is_system_role": True
    },

    # Request Module
    {
        "name": "Request Read",
        "code": "request_read",
        "description": "Can view requests",
        "module": "request",
        "level": "read",
        "permissions": [Permissions.REQUEST_READ],
        "is_system_role": True
    },
    {
        "name": "Request Read & Create",
        "code": "request_read_create",
        "description": "Can view and create requests",
        "module": "request",
        "level": "read_create",
        "permissions": [Permissions.REQUEST_READ, Permissions.REQUEST_CREATE],
        "is_system_role": True
    },
    {
        "name": "Request Agent",
        "code": "request_agent",
        "description": "Can view, create, update, approve, and resolve requests",
        "module": "request",
        "level": "agent",
        "permissions": [
            Permissions.REQUEST_READ,
            Permissions.REQUEST_CREATE,
            Permissions.REQUEST_UPDATE,
            Permissions.REQUEST_APPROVE,
            Permissions.REQUEST_RESOLVE
        ],
        "is_system_role": True
    },
    {
        "name": "Request Admin",
        "code": "request_admin",
        "description": "Full control over requests",
        "module": "request",
        "level": "admin",
        "permissions": [Permissions.REQUEST_ADMIN],
        "is_system_role": True
    },

    # User Module
    {
        "name": "User Read",
        "code": "user_read",
        "description": "Can view users",
        "module": "user",
        "level": "read",
        "permissions": [Permissions.USER_READ],
        "is_system_role": True
    },
    {
        "name": "User Read & Create",
        "code": "user_read_create",
        "description": "Can view and create users",
        "module": "user",
        "level": "read_create",
        "permissions": [Permissions.USER_READ, Permissions.USER_CREATE],
        "is_system_role": True
    },
    {
        "name": "User Agent",
        "code": "user_agent",
        "description": "Can view, create, and update users",
        "module": "user",
        "level": "agent",
        "permissions": [
            Permissions.USER_READ,
            Permissions.USER_CREATE,
            Permissions.USER_UPDATE
        ],
        "is_system_role": True
    },
    {
        "name": "User Admin",
        "code": "user_admin",
        "description": "Full control over users",
        "module": "user",
        "level": "admin",
        "permissions": [Permissions.USER_ADMIN],
        "is_system_role": True
    },

    # Company Module
    {
        "name": "Company Read",
        "code": "company_read",
        "description": "Can view companies",
        "module": "company",
        "level": "read",
        "permissions": [Permissions.COMPANY_READ],
        "is_system_role": True
    },
    {
        "name": "Company Read & Create",
        "code": "company_read_create",
        "description": "Can view and create companies",
        "module": "company",
        "level": "read_create",
        "permissions": [Permissions.COMPANY_READ, Permissions.COMPANY_CREATE],
        "is_system_role": True
    },
    {
        "name": "Company Agent",
        "code": "company_agent",
        "description": "Can view, create, and update companies",
        "module": "company",
        "level": "agent",
        "permissions": [
            Permissions.COMPANY_READ,
            Permissions.COMPANY_CREATE,
            Permissions.COMPANY_UPDATE
        ],
        "is_system_role": True
    },
    {
        "name": "Company Admin",
        "code": "company_admin",
        "description": "Full control over companies",
        "module": "company",
        "level": "admin",
        "permissions": [Permissions.COMPANY_ADMIN],
        "is_system_role": True
    },

    # Support Group Module
    {
        "name": "Support Group Read",
        "code": "support_group_read",
        "description": "Can view support groups",
        "module": "support_group",
        "level": "read",
        "permissions": [Permissions.SUPPORT_GROUP_READ],
        "is_system_role": True
    },
    {
        "name": "Support Group Read & Create",
        "code": "support_group_read_create",
        "description": "Can view and create support groups",
        "module": "support_group",
        "level": "read_create",
        "permissions": [Permissions.SUPPORT_GROUP_READ, Permissions.SUPPORT_GROUP_CREATE],
        "is_system_role": True
    },
    {
        "name": "Support Group Agent",
        "code": "support_group_agent",
        "description": "Can view, create, and update support groups",
        "module": "support_group",
        "level": "agent",
        "permissions": [
            Permissions.SUPPORT_GROUP_READ,
            Permissions.SUPPORT_GROUP_CREATE,
            Permissions.SUPPORT_GROUP_UPDATE
        ],
        "is_system_role": True
    },
    {
        "name": "Support Group Admin",
        "code": "support_group_admin",
        "description": "Full control over support groups",
        "module": "support_group",
        "level": "admin",
        "permissions": [Permissions.SUPPORT_GROUP_ADMIN],
        "is_system_role": True
    },

    # Category Module
    {
        "name": "Category Read",
        "code": "category_read",
        "description": "Can view categories",
        "module": "category",
        "level": "read",
        "permissions": [Permissions.CATEGORY_READ],
        "is_system_role": True
    },
    {
        "name": "Category Read & Create",
        "code": "category_read_create",
        "description": "Can view and create categories",
        "module": "category",
        "level": "read_create",
        "permissions": [Permissions.CATEGORY_READ, Permissions.CATEGORY_CREATE],
        "is_system_role": True
    },
    {
        "name": "Category Agent",
        "code": "category_agent",
        "description": "Can view, create, and update categories",
        "module": "category",
        "level": "agent",
        "permissions": [
            Permissions.CATEGORY_READ,
            Permissions.CATEGORY_CREATE,
            Permissions.CATEGORY_UPDATE
        ],
        "is_system_role": True
    },
    {
        "name": "Category Admin",
        "code": "category_admin",
        "description": "Full control over categories",
        "module": "category",
        "level": "admin",
        "permissions": [Permissions.CATEGORY_ADMIN],
        "is_system_role": True
    },

    # Dashboard Module
    {
        "name": "Dashboard View",
        "code": "dashboard_view",
        "description": "Can view dashboards",
        "module": "dashboard",
        "level": "read",
        "permissions": [Permissions.DASHBOARD_VIEW],
        "is_system_role": True
    },
    {
        "name": "Dashboard Admin",
        "code": "dashboard_admin",
        "description": "Full control over dashboards",
        "module": "dashboard",
        "level": "admin",
        "permissions": [Permissions.DASHBOARD_ADMIN],
        "is_system_role": True
    },

    # Role Module
    {
        "name": "Role Read",
        "code": "role_read",
        "description": "Can view roles",
        "module": "role",
        "level": "read",
        "permissions": [Permissions.ROLE_READ],
        "is_system_role": True
    },
    {
        "name": "Role Admin",
        "code": "role_admin",
        "description": "Full control over roles",
        "module": "role",
        "level": "admin",
        "permissions": [Permissions.ROLE_ADMIN],
        "is_system_role": True
    },

    # Permission Group Module
    {
        "name": "Permission Group Read",
        "code": "permission_group_read",
        "description": "Can view permission groups",
        "module": "permission_group",
        "level": "read",
        "permissions": [Permissions.PERMISSION_GROUP_READ],
        "is_system_role": True
    },
    {
        "name": "Permission Group Admin",
        "code": "permission_group_admin",
        "description": "Full control over permission groups",
        "module": "permission_group",
        "level": "admin",
        "permissions": [Permissions.PERMISSION_GROUP_ADMIN],
        "is_system_role": True
    },
]


async def seed_default_roles(db: AsyncSession, tenant_id: UUID) -> None:
    """
    Seed default roles for a tenant.
    This should be called after tenant creation.

    Args:
        db: Database session
        tenant_id: Tenant UUID
    """
    for role_data in DEFAULT_ROLES:
        # Check if role already exists for this tenant
        stmt = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.code == role_data["code"],
            Role.is_deleted == False
        )
        result = await db.execute(stmt)
        existing_role = result.scalar_one_or_none()

        if not existing_role:
            # Create role
            role = Role(
                tenant_id=tenant_id,
                name=role_data["name"],
                code=role_data["code"],
                description=role_data["description"],
                module=role_data["module"],
                level=role_data["level"],
                permissions=role_data["permissions"],
                is_system_role=role_data["is_system_role"]
            )
            db.add(role)

    await db.commit()
    print(f"Seeded {len(DEFAULT_ROLES)} default roles for tenant {tenant_id}")


async def get_role_by_code(db: AsyncSession, tenant_id: UUID, code: str) -> Role | None:
    """Helper to get a role by code"""
    stmt = select(Role).where(
        Role.tenant_id == tenant_id,
        Role.code == code,
        Role.is_deleted == False
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
