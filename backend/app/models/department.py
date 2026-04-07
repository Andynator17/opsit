"""Department model"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Department(Base, BaseModelMixin):
    """Department within a company"""

    __tablename__ = "departments"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    parent_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    # Relationships
    company = relationship("Company", foreign_keys=[company_id])
    manager = relationship("User", foreign_keys=[manager_id])
    parent_department = relationship("Department", remote_side="Department.id", foreign_keys=[parent_department_id])

    __table_args__ = (
        Index("idx_departments_tenant_company", "tenant_id", "company_id"),
    )

    def __repr__(self):
        return f"<Department {self.name}>"
