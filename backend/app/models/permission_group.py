"""
Permission Group Model

Permission Groups define what users CAN DO.
Users inherit ALL roles from their permission groups.

Example:
  Permission Group: "Helpdesk Agent"
    ├─ Roles: Incident Agent, Request Agent, Task Agent
    └─ Members: [User A, User B, User C]
"""

from sqlalchemy import Column, String, Text, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin


# Association table: permission_group ↔ user (many-to-many)
permission_group_members = Table(
    'permission_group_members',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default='gen_random_uuid()'),
    Column('permission_group_id', UUID(as_uuid=True), ForeignKey('permission_groups.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', nullable=False, server_default='NOW()'),
)


# Association table: permission_group ↔ role (many-to-many)
permission_group_roles = Table(
    'permission_group_roles',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default='gen_random_uuid()'),
    Column('permission_group_id', UUID(as_uuid=True), ForeignKey('permission_groups.id', ondelete='CASCADE'), nullable=False),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', nullable=False, server_default='NOW()'),
)


class PermissionGroup(Base, BaseModelMixin):
    """Permission Group model - Defines what users can do"""

    __tablename__ = "permission_groups"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Group Details
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Relationships
    members = relationship(
        "User",
        secondary=permission_group_members,
        back_populates="permission_groups",
        lazy="selectin"
    )

    roles = relationship(
        "Role",
        secondary=permission_group_roles,
        back_populates="permission_groups",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<PermissionGroup {self.name}>"
