"""sys_ui_element — Fields within a Form Section"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysUiElement(Base, BaseModelMixin):
    """Individual field/element placed in a form section."""

    __tablename__ = "sys_ui_element"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sys_ui_section.id"), nullable=False)
    field_name = Column(String(100), nullable=True)  # references sys_dictionary.column_name
    element_type = Column(String(30), nullable=False, default="field")  # field, separator, annotation
    sequence = Column(Integer, default=100, nullable=False)
    column_index = Column(Integer, default=1, nullable=False)  # 1 or 2
    annotation_text = Column(Text, nullable=True)
    span = Column(Integer, default=1, nullable=False)  # 1 or 2 (column span)
