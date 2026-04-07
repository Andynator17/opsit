"""User model"""
from sqlalchemy import Column, String, Boolean, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class User(Base, BaseModelMixin):
    """User model"""

    __tablename__ = "users"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    primary_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Authentication
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    email_secondary = Column(String(255))
    password_hash = Column(String(255))

    # Personal Information
    employee_id = Column(String(50), index=True)
    salutation = Column(String(20))  # Mr, Ms, Mrs, Dr, Prof, etc.
    title = Column(String(50))  # Academic or professional title
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(255))  # Computed or set
    gender = Column(String(20))  # male, female, other, prefer_not_to_say

    # Contact Information
    phone = Column(String(50))
    phone_secondary = Column(String(50))
    mobile = Column(String(50))

    # Work Information
    job_title = Column(String(100))
    department = Column(String(100), index=True)  # Legacy string field
    location = Column(String(100), index=True)  # Legacy string field
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)

    # User Type & Roles
    user_type = Column(String(50), nullable=False, default='employee')  # employee, contractor, external, service_account, system
    is_vip = Column(Boolean, nullable=False, default=False)
    is_support_agent = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)

    # Preferences
    language = Column(String(10), nullable=False, default='en')
    timezone = Column(String(50), nullable=False, default='UTC')
    avatar_url = Column(String(500))

    # Authentication
    auth_provider = Column(String(50), nullable=False, default='local')
    last_login = Column(TIMESTAMP(timezone=True))
    password_changed_at = Column(TIMESTAMP(timezone=True))
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(TIMESTAMP(timezone=True))

    # MFA
    mfa_enabled = Column(Boolean, nullable=False, default=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    primary_company = relationship("Company", back_populates="users", foreign_keys=[primary_company_id])
    department_rel = relationship("Department", foreign_keys=[department_id])
    location_rel = relationship("Location", foreign_keys=[location_id])

    # RBAC Relationships
    permission_groups = relationship(
        "PermissionGroup",
        secondary="permission_group_members",
        back_populates="members"
    )
    # support_groups relationship already defined in backref from SupportGroup model
