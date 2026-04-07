"""sys_choice — Choice/Value Lists (ServiceNow-style)"""
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import BaseModelMixin


class SysChoice(Base, BaseModelMixin):
    """Predefined dropdown/choice values for fields."""

    __tablename__ = "sys_choice"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    table_name = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    value = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)
    sequence = Column(Integer, default=100, nullable=False)
    sys_class_name = Column(String(50), nullable=True)
    dependent_field = Column(String(100), nullable=True)
    dependent_value = Column(String(255), nullable=True)
    color = Column(String(20), nullable=True)

    __table_args__ = (
        Index("idx_sys_choice_lookup", "tenant_id", "table_name", "field_name", "sys_class_name"),
    )
