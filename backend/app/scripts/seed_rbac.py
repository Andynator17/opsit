"""
Seed script for RBAC (Roles and Permission Groups)

Creates default roles and permission groups for a fresh OpsIT installation.
Run this after running the RBAC migration.

Usage:
    python -m app.scripts.seed_rbac
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.role import Role
from app.models.permission_group import PermissionGroup


# Define default roles with their permissions
DEFAULT_ROLES = [
    # Incident Management Roles
    {
        "name": "Incident Reader",
        "code": "incident_read",
        "description": "Can view incidents",
        "module": "incident",
        "level": "read",
        "permissions": ["incident.view", "incident.list"],
        "is_system_role": True,
    },
    {
        "name": "Incident Agent",
        "code": "incident_agent",
        "description": "Can manage assigned incidents",
        "module": "incident",
        "level": "agent",
        "permissions": [
            "incident.view",
            "incident.list",
            "incident.create",
            "incident.update",
            "incident.assign",
            "incident.resolve",
            "incident.comment",
        ],
        "is_system_role": True,
    },
    {
        "name": "Incident Admin",
        "code": "incident_admin",
        "description": "Full control over incidents",
        "module": "incident",
        "level": "admin",
        "permissions": ["incident.*"],
        "is_system_role": True,
    },
    # Request Management Roles
    {
        "name": "Request Reader",
        "code": "request_read",
        "description": "Can view requests",
        "module": "request",
        "level": "read",
        "permissions": ["request.view", "request.list"],
        "is_system_role": True,
    },
    {
        "name": "Request Agent",
        "code": "request_agent",
        "description": "Can manage assigned requests",
        "module": "request",
        "level": "agent",
        "permissions": [
            "request.view",
            "request.list",
            "request.create",
            "request.update",
            "request.assign",
            "request.fulfill",
            "request.approve",
            "request.comment",
        ],
        "is_system_role": True,
    },
    {
        "name": "Request Admin",
        "code": "request_admin",
        "description": "Full control over requests",
        "module": "request",
        "level": "admin",
        "permissions": ["request.*"],
        "is_system_role": True,
    },
    # User Management Roles
    {
        "name": "User Reader",
        "code": "user_read",
        "description": "Can view users",
        "module": "user",
        "level": "read",
        "permissions": ["user.view", "user.list"],
        "is_system_role": True,
    },
    {
        "name": "User Admin",
        "code": "user_admin",
        "description": "Full control over users",
        "module": "user",
        "level": "admin",
        "permissions": ["user.*"],
        "is_system_role": True,
    },
    # Company Management Roles
    {
        "name": "Company Reader",
        "code": "company_read",
        "description": "Can view companies",
        "module": "company",
        "level": "read",
        "permissions": ["company.view", "company.list"],
        "is_system_role": True,
    },
    {
        "name": "Company Admin",
        "code": "company_admin",
        "description": "Full control over companies",
        "module": "company",
        "level": "admin",
        "permissions": ["company.*"],
        "is_system_role": True,
    },
    # Knowledge Base Roles
    {
        "name": "Knowledge Reader",
        "code": "knowledge_read",
        "description": "Can view knowledge articles",
        "module": "knowledge",
        "level": "read",
        "permissions": ["knowledge.view", "knowledge.list", "knowledge.search"],
        "is_system_role": True,
    },
    {
        "name": "Knowledge Author",
        "code": "knowledge_author",
        "description": "Can create and edit knowledge articles",
        "module": "knowledge",
        "level": "agent",
        "permissions": [
            "knowledge.view",
            "knowledge.list",
            "knowledge.search",
            "knowledge.create",
            "knowledge.update",
            "knowledge.publish",
        ],
        "is_system_role": True,
    },
    # System Administration
    {
        "name": "System Administrator",
        "code": "system_admin",
        "description": "Full system administration rights",
        "module": "system",
        "level": "admin",
        "permissions": ["*"],
        "is_system_role": True,
    },
]


# Define default permission groups
DEFAULT_PERMISSION_GROUPS = [
    {
        "name": "System Administrators",
        "description": "Full system access - can manage everything",
        "role_codes": ["system_admin"],
    },
    {
        "name": "Helpdesk Agents",
        "description": "Standard helpdesk agents - can manage incidents and requests",
        "role_codes": [
            "incident_agent",
            "request_agent",
            "knowledge_read",
            "user_read",
            "company_read",
        ],
    },
    {
        "name": "Helpdesk Managers",
        "description": "Helpdesk team leads - full control over tickets",
        "role_codes": [
            "incident_admin",
            "request_admin",
            "knowledge_author",
            "user_read",
            "company_read",
        ],
    },
    {
        "name": "End Users",
        "description": "Standard end users - can create and view their own tickets",
        "role_codes": [
            "incident_read",
            "request_read",
            "knowledge_read",
        ],
    },
    {
        "name": "Knowledge Authors",
        "description": "Can create and manage knowledge base articles",
        "role_codes": [
            "knowledge_author",
            "incident_read",
            "request_read",
        ],
    },
    {
        "name": "User Administrators",
        "description": "Can manage users and companies",
        "role_codes": [
            "user_admin",
            "company_admin",
            "incident_read",
            "request_read",
        ],
    },
]


async def seed_roles_and_groups():
    """Seed default roles and permission groups for all tenants"""
    async with AsyncSessionLocal() as session:
        # Get all tenants
        result = await session.execute(
            select(Tenant).where(Tenant.is_deleted == False)
        )
        tenants = result.scalars().all()

        if not tenants:
            print("ERROR: No tenants found. Please create a tenant first.")
            return

        for tenant in tenants:
            print(f"\nSeeding RBAC for tenant: {tenant.name} ({tenant.subdomain})")

            # Create roles
            print("\nCreating roles...")
            role_map = {}  # Map role codes to role objects

            for role_data in DEFAULT_ROLES:
                # Check if role already exists
                existing_role = await session.execute(
                    select(Role).where(
                        Role.tenant_id == tenant.id,
                        Role.code == role_data["code"],
                        Role.is_deleted == False,
                    )
                )
                existing = existing_role.scalar_one_or_none()

                if existing:
                    print(f"  SKIP: Role '{role_data['name']}' already exists")
                    role_map[role_data["code"]] = existing
                    continue

                # Create new role
                role = Role(
                    tenant_id=tenant.id,
                    name=role_data["name"],
                    code=role_data["code"],
                    description=role_data["description"],
                    module=role_data["module"],
                    level=role_data["level"],
                    permissions=role_data["permissions"],
                    is_system_role=role_data["is_system_role"],
                )
                session.add(role)
                role_map[role_data["code"]] = role
                print(f"  OK: Created role: {role_data['name']} ({role_data['code']})")

            await session.commit()

            # Create permission groups
            print("\nCreating permission groups...")

            for group_data in DEFAULT_PERMISSION_GROUPS:
                # Check if permission group already exists
                existing_group = await session.execute(
                    select(PermissionGroup).where(
                        PermissionGroup.tenant_id == tenant.id,
                        PermissionGroup.name == group_data["name"],
                        PermissionGroup.is_deleted == False,
                    )
                )
                existing = existing_group.scalar_one_or_none()

                if existing:
                    print(f"  SKIP: Permission group '{group_data['name']}' already exists")
                    continue

                # Create new permission group
                perm_group = PermissionGroup(
                    tenant_id=tenant.id,
                    name=group_data["name"],
                    description=group_data["description"],
                )

                # Assign roles to group
                for role_code in group_data["role_codes"]:
                    if role_code in role_map:
                        perm_group.roles.append(role_map[role_code])

                session.add(perm_group)
                print(f"  OK: Created permission group: {group_data['name']} ({len(group_data['role_codes'])} roles)")

            await session.commit()

        print("\nRBAC seeding completed successfully!")
        print("\nSummary:")
        print(f"   - {len(DEFAULT_ROLES)} roles created")
        print(f"   - {len(DEFAULT_PERMISSION_GROUPS)} permission groups created")
        print(f"   - Seeded for {len(tenants)} tenant(s)")


if __name__ == "__main__":
    print("Starting RBAC seed script...\n")
    asyncio.run(seed_roles_and_groups())
