"""sys_ui_list — List View Column Configuration"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysUiList(Base, BaseModelMixin):
    """Column configuration for a table's list/table view."""

    __tablename__ = "sys_ui_list"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    view_id = Column(UUID(as_uuid=True), ForeignKey("sys_ui_view.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    sequence = Column(Integer, default=100, nullable=False)
    sort_direction = Column(String(4), nullable=True)  # asc, desc, NULL
    sort_priority = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
