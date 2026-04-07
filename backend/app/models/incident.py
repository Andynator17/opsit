"""Incident model - ITIL compliant incident management"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base
from app.models.base import BaseModelMixin


class Incident(Base, BaseModelMixin):
    """Incident model - ITIL incident management"""

    __tablename__ = "incidents"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Ticket Identification
    incident_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    category = Column(String(100), nullable=False, index=True)  # e.g., "Hardware", "Software", "Network"
    subcategory = Column(String(100))  # e.g., "Laptop", "Desktop", "Printer"
    item = Column(String(100))  # Further classification

    # Priority & Impact
    urgency = Column(String(20), nullable=False, default="medium")  # low, medium, high, critical
    impact = Column(String(20), nullable=False, default="medium")  # low, medium, high, critical
    priority = Column(String(20), nullable=False, index=True)  # low, medium, high, critical (calculated)

    # Status & Workflow
    status = Column(String(50), nullable=False, default="new", index=True)  # new, assigned, in_progress, pending, resolved, closed, cancelled
    status_reason = Column(String(255))  # Reason for current status

    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)  # Individual assignee
    assigned_group_id = Column(UUID(as_uuid=True), ForeignKey("support_groups.id"), index=True)  # Support group

    # Reporter & Affected Users (ITIL distinction)
    opened_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # Who created the ticket in the system
    caller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)  # Who reported the issue (phone/email)
    affected_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)  # User affected by the incident
    reported_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # Deprecated: use opened_by_id
    reported_date = Column(DateTime(timezone=True), nullable=False)

    # Contact Information
    contact_type = Column(String(50), default="phone")  # phone, email, portal, chat, walk-in

    # Resolution
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_date = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    resolution_code = Column(String(100))  # e.g., "fixed", "workaround", "known_error"

    # Closure
    closed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    closed_date = Column(DateTime(timezone=True))

    # SLA Management
    sla_target_resolve = Column(DateTime(timezone=True))  # When incident must be resolved
    sla_target_respond = Column(DateTime(timezone=True))  # When first response is due
    sla_breach = Column(String(20), default="none")  # none, warning, breached
    response_time_minutes = Column(Integer)  # Actual time to first response
    resolution_time_minutes = Column(Integer)  # Actual time to resolution

    # Additional Details
    root_cause = Column(Text)  # Root cause analysis
    workaround = Column(Text)  # Temporary workaround
    affected_services = Column(JSON)  # List of affected services/systems
    affected_users_count = Column(Integer, default=1)  # Number of users affected

    # External References
    related_problem_id = Column(UUID(as_uuid=True))  # Link to Problem (future)
    related_change_id = Column(UUID(as_uuid=True))  # Link to Change (future)
    external_ticket_id = Column(String(100))  # Reference to external system

    # Custom Fields
    custom_fields = Column(JSON)  # Extensibility for custom data

    # Relationships
    opened_by = relationship("User", foreign_keys=[opened_by_id], lazy="joined")
    caller = relationship("User", foreign_keys=[caller_id], lazy="joined")
    affected_user = relationship("User", foreign_keys=[affected_user_id], lazy="joined")
    reported_by = relationship("User", foreign_keys=[reported_by_id], lazy="joined")  # Deprecated
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], lazy="joined")
    assigned_group = relationship("SupportGroup", foreign_keys=[assigned_group_id], lazy="joined")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id], lazy="joined")
    closed_by = relationship("User", foreign_keys=[closed_by_id], lazy="joined")
    company = relationship("Company", lazy="joined")

    def __repr__(self):
        return f"<Incident {self.incident_number}: {self.title}>"

    @staticmethod
    def calculate_priority(urgency: str, impact: str) -> str:
        """
        Calculate priority based on urgency and impact matrix
        ITIL-compliant priority calculation
        """
        priority_matrix = {
            ("critical", "critical"): "critical",
            ("critical", "high"): "critical",
            ("critical", "medium"): "high",
            ("critical", "low"): "high",
            ("high", "critical"): "critical",
            ("high", "high"): "high",
            ("high", "medium"): "high",
            ("high", "low"): "medium",
            ("medium", "critical"): "high",
            ("medium", "high"): "high",
            ("medium", "medium"): "medium",
            ("medium", "low"): "low",
            ("low", "critical"): "high",
            ("low", "high"): "medium",
            ("low", "medium"): "low",
            ("low", "low"): "low",
        }
        return priority_matrix.get((urgency, impact), "medium")
