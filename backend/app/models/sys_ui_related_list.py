"""sys_ui_related_list — Related Lists on Forms"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysUiRelatedList(Base, BaseModelMixin):
    """Configures which related lists appear on a form view."""

    __tablename__ = "sys_ui_related_list"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    view_id = Column(UUID(as_uuid=True), ForeignKey("sys_ui_view.id"), nullable=False)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("sys_relationship.id"), nullable=False)
    title = Column(String(255), nullable=False)
    sequence = Column(Integer, default=100, nullable=False)
    display_fields = Column(JSON, nullable=False, default=list)  # ["number", "short_description", "status"]
    filter_condition = Column(JSON, nullable=True)  # {"sys_class_name": "incident"}
    max_rows = Column(Integer, default=20, nullable=False)
    sys_class_name = Column(String(50), nullable=True)
