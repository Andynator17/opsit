"""Request model - ITIL service request management"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base
from app.models.base import BaseModelMixin


class Request(Base, BaseModelMixin):
    """Service Request model - ITIL request management"""

    __tablename__ = "requests"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Request Identification
    request_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    category = Column(String(100), nullable=False, index=True)  # e.g., "Access", "Hardware", "Software"
    subcategory = Column(String(100))  # e.g., "VPN Access", "New Laptop"
    catalog_item = Column(String(100))  # Link to service catalog item

    # Priority
    urgency = Column(String(20), nullable=False, default="medium")  # low, medium, high, critical
    priority = Column(String(20), nullable=False, default="medium", index=True)  # low, medium, high, critical

    # Status & Workflow
    status = Column(String(50), nullable=False, default="submitted", index=True)
    # submitted, pending_approval, approved, rejected, in_progress, fulfilled, closed, cancelled
    status_reason = Column(String(255))

    # Requester (End User)
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    requested_date = Column(DateTime(timezone=True), nullable=False)
    requested_for_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # If request is for someone else
    contact_type = Column(String(50), default="portal")  # phone, email, portal, chat

    # Approval Process
    requires_approval = Column(Boolean, nullable=False, default=False)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_date = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    rejection_reason = Column(Text)

    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    assigned_group_id = Column(UUID(as_uuid=True))  # Support group

    # Fulfillment
    fulfilled_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    fulfilled_date = Column(DateTime(timezone=True))
    fulfillment_notes = Column(Text)

    # Closure
    closed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    closed_date = Column(DateTime(timezone=True))
    closure_notes = Column(Text)

    # SLA Management
    sla_target_fulfill = Column(DateTime(timezone=True))  # When request must be fulfilled
    sla_breach = Column(String(20), default="none")  # none, warning, breached
    fulfillment_time_minutes = Column(Integer)  # Actual time to fulfillment

    # Additional Details
    business_justification = Column(Text)  # Why this request is needed
    cost_center = Column(String(100))  # For budget tracking
    estimated_cost = Column(String(50))  # Estimated cost
    quantity = Column(Integer, default=1)  # How many items requested

    # Custom Fields
    custom_fields = Column(JSON)

    # Relationships
    requested_by = relationship("User", foreign_keys=[requested_by_id], lazy="joined")
    requested_for = relationship("User", foreign_keys=[requested_for_id], lazy="joined")
    approved_by = relationship("User", foreign_keys=[approved_by_id], lazy="joined")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], lazy="joined")
    fulfilled_by = relationship("User", foreign_keys=[fulfilled_by_id], lazy="joined")
    closed_by = relationship("User", foreign_keys=[closed_by_id], lazy="joined")
    company = relationship("Company", lazy="joined")

    def __repr__(self):
        return f"<Request {self.request_number}: {self.title}>"
