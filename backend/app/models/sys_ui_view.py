"""sys_ui_view — View Definitions (ServiceNow-style)"""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysUiView(Base, BaseModelMixin):
    """Different views/perspectives of a table's form and list."""

    __tablename__ = "sys_ui_view"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False)  # "default", "ess", "compact"
    title = Column(String(255), nullable=False)
    table_name = Column(String(100), nullable=False)
    sys_class_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_sys_ui_view_lookup", "tenant_id", "table_name", "name", "sys_class_name", unique=True),
    )
