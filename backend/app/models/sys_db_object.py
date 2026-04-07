"""sys_db_object — Table Registry (ServiceNow-style)"""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysDbObject(Base, BaseModelMixin):
    """Registry of all tables in the system. Enables table inheritance, display fields, and module assignment."""

    __tablename__ = "sys_db_object"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    plural_label = Column(String(255), nullable=True)
    super_class = Column(String(100), nullable=True)
    display_field = Column(String(100), nullable=True)
    number_prefix = Column(String(10), nullable=True)
    is_extendable = Column(Boolean, default=True, nullable=False)
    module = Column(String(50), nullable=True)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_sys_db_object_tenant_name", "tenant_id", "name", unique=True),
    )
