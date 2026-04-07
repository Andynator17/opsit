"""Location model"""
from sqlalchemy import Column, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Location(Base, BaseModelMixin):
    """Physical location belonging to a company"""

    __tablename__ = "locations"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Relationships
    company = relationship("Company", foreign_keys=[company_id])

    __table_args__ = (
        Index("idx_locations_tenant_company", "tenant_id", "company_id"),
    )

    def __repr__(self):
        return f"<Location {self.name}>"
