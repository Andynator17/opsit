"""sys_dictionary — Field Dictionary (ServiceNow-style)"""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysDictionary(Base, BaseModelMixin):
    """Central field definition for every column on every table."""

    __tablename__ = "sys_dictionary"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)  # string, text, integer, boolean, reference, choice, datetime, etc.
    max_length = Column(Integer, nullable=True)
    is_mandatory = Column(Boolean, default=False, nullable=False)
    is_read_only = Column(Boolean, default=False, nullable=False)
    is_display = Column(Boolean, default=False, nullable=False)
    default_value = Column(String(500), nullable=True)
    reference_table = Column(String(100), nullable=True)
    reference_display_field = Column(String(100), nullable=True)
    hint = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=100, nullable=False)
    sys_class_name = Column(String(50), nullable=True)  # NULL = all subtypes
    is_system = Column(Boolean, default=False, nullable=False)
    column_exists = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_sys_dict_lookup", "tenant_id", "table_name", "column_name", "sys_class_name"),
        Index("idx_sys_dict_table", "tenant_id", "table_name"),
    )
