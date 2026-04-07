"""Portal model for self-service portals"""
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Portal(Base, BaseModelMixin):
    """Self-service portal configuration"""

    __tablename__ = "portals"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Identity
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    # Audience
    audience_type = Column(String(50), nullable=False, default="internal")
    # "internal" = all users in tenant
    # "company" = specific company only
    # "external" = external customers (future)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(20), default="#667eea")
    accent_color = Column(String(20), default="#764ba2")
    welcome_title = Column(String(255))
    welcome_message = Column(Text)

    # Configuration
    enabled_modules = Column(JSONB, default=list)
    visible_categories = Column(JSONB, default=list)
    default_ticket_type = Column(String(50), default="incident")

    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    tenant = relationship("Tenant")
    company = relationship("Company")
