"""sys_ui_section — Form Sections within a View"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysUiSection(Base, BaseModelMixin):
    """A section/card within a form view."""

    __tablename__ = "sys_ui_section"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    view_id = Column(UUID(as_uuid=True), ForeignKey("sys_ui_view.id"), nullable=False)
    title = Column(String(255), nullable=False)
    section_type = Column(String(30), nullable=False, default="fields")  # fields, related_list, activity, attachments
    columns = Column(Integer, default=2, nullable=False)
    sequence = Column(Integer, default=100, nullable=False)
    is_expanded = Column(Boolean, default=True, nullable=False)
    position = Column(String(10), default="full", nullable=False)  # left, right, full
    sys_class_name = Column(String(50), nullable=True)
