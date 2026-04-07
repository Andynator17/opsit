"""Company model"""
from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Company(Base, BaseModelMixin):
    """Company (multi-company support - USP!)"""

    __tablename__ = "companies"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Basic Information
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    company_code = Column(String(50))

    # Company Type
    company_type = Column(String(50), nullable=False, default='internal')
    parent_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))

    # Contact Information
    primary_email = Column(String(255))
    primary_phone = Column(String(50))
    website = Column(String(255))

    # Address
    address_line1 = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))

    # Business Details
    industry = Column(String(100))
    employee_count = Column(Integer)

    # Contract & SLA
    contract_start_date = Column(Date)
    contract_end_date = Column(Date)
    support_tier = Column(String(50))

    # Branding (for portal)
    logo_url = Column(String(500))
    primary_color = Column(String(20))
    secondary_color = Column(String(20))
    portal_subdomain = Column(String(100), unique=True)

    # Main IT Company flag (only one per tenant)
    is_main_it_company = Column(Boolean, nullable=False, default=False)

    # Status
    status = Column(String(50), nullable=False, default='active')

    # Custom Fields
    custom_fields = Column(JSONB)

    # Relationships
    tenant = relationship("Tenant", back_populates="companies")
    users = relationship("User", back_populates="primary_company", foreign_keys="User.primary_company_id")
