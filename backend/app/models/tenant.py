"""Tenant model"""
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Tenant(Base, BaseModelMixin):
    """Tenant (SaaS instance)"""

    __tablename__ = "tenants"

    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default='active')
    plan = Column(String(50), nullable=False, default='starter')
    max_users = Column(Integer, default=10)
    max_storage_gb = Column(Integer, default=10)
    custom_domain = Column(String(255))
    branding = Column(JSONB)
    settings = Column(JSONB)
    subscription_ends_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    companies = relationship("Company", back_populates="tenant", lazy="selectin")
    users = relationship("User", back_populates="tenant", lazy="selectin")
    tasks = relationship("Task", back_populates="tenant", lazy="selectin")
