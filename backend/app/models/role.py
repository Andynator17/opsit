"""
Role Model

Defines granular permissions per module.
Format: {Module} {Level}
Levels: Read, Read&Create, Agent, Admin

Examples:
- incident_read: Can view incidents
- incident_read_create: Can view and create incidents
- incident_agent: Can view, create, update, resolve incidents
- incident_admin: Full control over incidents
"""

from sqlalchemy import Column, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin


class Role(Base, BaseModelMixin):
    """Role model - Granular permissions per module"""

    __tablename__ = "roles"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Role Details
    name = Column(String(100), nullable=False)  # e.g., "Incident Agent", "Request Admin"
    code = Column(String(100), nullable=False)  # e.g., "incident_agent", "request_admin" (snake_case, unique)
    description = Column(Text)

    # Module & Level
    module = Column(String(50), nullable=False)  # incident, request, task, user, company, etc.
    level = Column(String(50), nullable=False)   # read, read_create, agent, admin

    # Permissions (JSONB array of permission strings)
    permissions = Column(JSON, nullable=False, default=list)
    """
    Examples:
    - incident_read: ["incident.view"]
    - incident_read_create: ["incident.view", "incident.create"]
    - incident_agent: ["incident.view", "incident.create", "incident.update", "incident.assign", "incident.resolve"]
    - incident_admin: ["incident.*"]  (all permissions)
    """

    # System Role Flag
    is_system_role = Column(Boolean, nullable=False, default=False)
    """System roles cannot be deleted or modified (created during initialization)"""

    # Relationships
    permission_groups = relationship(
        "PermissionGroup",
        secondary="permission_group_roles",
        back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.code}>"
