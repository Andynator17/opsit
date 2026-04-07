"""Permission checking utilities for RBAC"""
from typing import List, Set
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.permission_group import PermissionGroup


async def get_user_permissions(user: User, db: AsyncSession) -> Set[str]:
    """
    Get all permissions for a user from their permission groups.
    Returns a set of permission strings.
    """
    if user.is_admin:
        # Admins have all permissions
        return {"*"}

    permissions: Set[str] = set()

    # Query permission groups with roles eagerly loaded
    stmt = select(PermissionGroup).options(
        selectinload(PermissionGroup.roles)
    ).join(
        PermissionGroup.members
    ).where(
        User.id == user.id,
        PermissionGroup.tenant_id == user.tenant_id,
        PermissionGroup.is_deleted == False
    )

    result = await db.execute(stmt)
    permission_groups = result.scalars().all()

    # Collect all permissions from all roles in all permission groups
    for group in permission_groups:
        for role in group.roles:
            if role.is_active and not role.is_deleted:
                permissions.update(role.permissions)

    return permissions


async def check_permission(user: User, required_permission: str, db: AsyncSession) -> bool:
    """
    Check if a user has a specific permission.
    Supports wildcard (*) for admins.
    """
    if user.is_admin:
        return True

    user_permissions = await get_user_permissions(user, db)

    # Check for wildcard (admin)
    if "*" in user_permissions:
        return True

    # Check for exact permission
    if required_permission in user_permissions:
        return True

    # Check for module-level wildcard (e.g., "incident.*" grants all incident permissions)
    module = required_permission.split(".")[0] if "." in required_permission else required_permission
    module_wildcard = f"{module}.*"
    if module_wildcard in user_permissions:
        return True

    return False


async def check_permissions(user: User, required_permissions: List[str], db: AsyncSession, require_all: bool = True) -> bool:
    """
    Check if a user has multiple permissions.

    Args:
        user: The user to check
        required_permissions: List of permissions to check
        db: Database session
        require_all: If True, user must have ALL permissions. If False, user needs at least ONE.
    """
    if user.is_admin:
        return True

    user_permissions = await get_user_permissions(user, db)

    if "*" in user_permissions:
        return True

    if require_all:
        # User must have ALL permissions
        for perm in required_permissions:
            has_perm = perm in user_permissions

            # Check module wildcard
            if not has_perm and "." in perm:
                module = perm.split(".")[0]
                has_perm = f"{module}.*" in user_permissions

            if not has_perm:
                return False
        return True
    else:
        # User needs at least ONE permission
        for perm in required_permissions:
            if perm in user_permissions:
                return True

            # Check module wildcard
            if "." in perm:
                module = perm.split(".")[0]
                if f"{module}.*" in user_permissions:
                    return True

        return False


class PermissionChecker:
    """Dependency for checking permissions in FastAPI routes"""

    def __init__(self, required_permissions: List[str], require_all: bool = True):
        """
        Initialize permission checker.

        Args:
            required_permissions: List of permissions required
            require_all: If True, user must have ALL permissions. If False, at least ONE.
        """
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Check if current user has required permissions"""
        has_permission = await check_permissions(
            current_user,
            self.required_permissions,
            db,
            self.require_all
        )

        if not has_permission:
            if self.require_all:
                detail = f"Missing required permissions: {', '.join(self.required_permissions)}"
            else:
                detail = f"Missing at least one of: {', '.join(self.required_permissions)}"

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )

        return current_user


def require_permission(permission: str):
    """
    Convenience function to create a single permission checker.

    Usage:
        @app.get("/incidents")
        async def get_incidents(user: User = Depends(require_permission("incident.read"))):
            ...
    """
    return PermissionChecker([permission], require_all=True)


def require_permissions(*permissions: str, require_all: bool = True):
    """
    Convenience function to create a multi-permission checker.

    Usage:
        @app.post("/incidents")
        async def create_incident(
            user: User = Depends(require_permissions("incident.create", "incident.read"))
        ):
            ...
    """
    return PermissionChecker(list(permissions), require_all=require_all)


def require_any_permission(*permissions: str):
    """
    Convenience function to require at least ONE of the given permissions.

    Usage:
        @app.get("/tickets")
        async def get_tickets(
            user: User = Depends(require_any_permission("incident.read", "request.read"))
        ):
            ...
    """
    return PermissionChecker(list(permissions), require_all=False)


# Standard permission definitions for reference
class Permissions:
    """Standard permission strings for the application"""

    # Incident permissions
    INCIDENT_READ = "incident.read"
    INCIDENT_CREATE = "incident.create"
    INCIDENT_UPDATE = "incident.update"
    INCIDENT_RESOLVE = "incident.resolve"
    INCIDENT_DELETE = "incident.delete"
    INCIDENT_ASSIGN = "incident.assign"
    INCIDENT_ADMIN = "incident.*"

    # Request permissions
    REQUEST_READ = "request.read"
    REQUEST_CREATE = "request.create"
    REQUEST_UPDATE = "request.update"
    REQUEST_APPROVE = "request.approve"
    REQUEST_RESOLVE = "request.resolve"
    REQUEST_DELETE = "request.delete"
    REQUEST_ADMIN = "request.*"

    # User permissions
    USER_READ = "user.read"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_ADMIN = "user.*"

    # Company permissions
    COMPANY_READ = "company.read"
    COMPANY_CREATE = "company.create"
    COMPANY_UPDATE = "company.update"
    COMPANY_DELETE = "company.delete"
    COMPANY_ADMIN = "company.*"

    # Role permissions
    ROLE_READ = "role.read"
    ROLE_CREATE = "role.create"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"
    ROLE_ADMIN = "role.*"

    # Permission Group permissions
    PERMISSION_GROUP_READ = "permission_group.read"
    PERMISSION_GROUP_CREATE = "permission_group.create"
    PERMISSION_GROUP_UPDATE = "permission_group.update"
    PERMISSION_GROUP_DELETE = "permission_group.delete"
    PERMISSION_GROUP_ADMIN = "permission_group.*"

    # Support Group permissions
    SUPPORT_GROUP_READ = "support_group.read"
    SUPPORT_GROUP_CREATE = "support_group.create"
    SUPPORT_GROUP_UPDATE = "support_group.update"
    SUPPORT_GROUP_DELETE = "support_group.delete"
    SUPPORT_GROUP_ADMIN = "support_group.*"

    # Category permissions
    CATEGORY_READ = "category.read"
    CATEGORY_CREATE = "category.create"
    CATEGORY_UPDATE = "category.update"
    CATEGORY_DELETE = "category.delete"
    CATEGORY_ADMIN = "category.*"

    # Dashboard permissions
    DASHBOARD_VIEW = "dashboard.view"
    DASHBOARD_ADMIN = "dashboard.*"

    # System-wide admin
    ADMIN_ALL = "*"
