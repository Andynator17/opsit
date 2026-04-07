"""sys_relationship — Table Relationships (Reference Tables)"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysRelationship(Base, BaseModelMixin):
    """Defines explicit relationships between tables (1:N and N:N)."""

    __tablename__ = "sys_relationship"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    parent_table = Column(String(100), nullable=False)
    child_table = Column(String(100), nullable=False)
    relationship_type = Column(String(20), nullable=False)  # one_to_many, many_to_many
    foreign_key_field = Column(String(100), nullable=True)  # For 1:N: FK column on child table
    join_table = Column(String(100), nullable=True)  # For M2M: association table name
    join_parent_field = Column(String(100), nullable=True)  # For M2M: FK pointing to parent
    join_child_field = Column(String(100), nullable=True)  # For M2M: FK pointing to child
    description = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_sys_rel_parent_child", "tenant_id", "parent_table", "child_table"),
    )
