"""Support Group model - Teams for ticket assignment"""
from sqlalchemy import Column, String, Text, ForeignKey, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


# Association table for group members (many-to-many)
group_members = Table(
    'group_members',
    Base.metadata,
    Column('group_id', UUID(as_uuid=True), ForeignKey('support_groups.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('is_team_lead', Boolean, default=False)
)


class SupportGroup(Base, BaseModelMixin):
    """Support Group model - Teams for ticket routing"""

    __tablename__ = "support_groups"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Group Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    email = Column(String(255))  # Group email (optional)

    # Assignment
    group_type = Column(String(50), default="support")  # support, operations, development, management
    assignment_method = Column(String(50), default="manual")  # manual, round_robin, load_balanced, skill_based

    # Manager
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id], lazy="joined")
    members = relationship("User", secondary=group_members, backref="support_groups", lazy="selectin")

    def __repr__(self):
        return f"<SupportGroup {self.name}>"
