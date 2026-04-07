"""
Task model - Central table for all ticket types (Incident, Request, Change, Problem, Task, Request Item)
Based on ServiceNow task table pattern - ITIL compliant
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base
from app.models.base import BaseModelMixin


class Task(Base, BaseModelMixin):
    """
    Task - Central table for all ticket types (ServiceNow pattern)

    All ticket types inherit from this table:
    - Incident (INC)
    - Request (REQ)
    - Change (CHG)
    - Problem (PRB)
    - Task (TASK)
    - Request Item (RITM)
    """

    __tablename__ = "tasks"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # System Fields
    sys_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)  # Unique system ID
    number = Column(String(40), unique=True, nullable=False)  # INC000000001 — idx in __table_args__
    sys_class_name = Column(String(50), nullable=False)  # incident, request, etc. — composite idx in __table_args__
    sys_created_on = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sys_updated_on = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Basic Information (Universal fields for ALL ticket types)
    short_description = Column(String(255), nullable=False)  # Title/Summary
    description = Column(Text)  # Detailed description

    # Company & User Fields (ITIL distinctions)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    opened_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Who opened the ticket
    caller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Who reported (might be different from opener)
    caller_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))  # Caller's company
    affected_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # User affected by issue
    affected_user_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))  # Affected user's company

    # Assignment
    assignment_group_id = Column(UUID(as_uuid=True), ForeignKey("support_groups.id"))
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reassignment_count = Column(Integer, default=0)  # Track how many times reassigned

    # Categorization
    category = Column(String(100), index=True)  # Hardware, Software, Network, etc.
    subcategory = Column(String(100))
    service_id = Column(UUID(as_uuid=True))  # Link to service catalog (future - no FK yet)
    channel = Column(String(50), default="web")  # web, phone, email, walk-in, self-service

    # Priority Matrix (ITIL)
    impact = Column(String(20), nullable=False)  # low, medium, high, critical
    urgency = Column(String(20), nullable=False)  # low, medium, high, critical
    priority = Column(String(20), nullable=False)  # Calculated from impact + urgency — idx in __table_args__

    # Status & Workflow
    status = Column(String(50), nullable=False)  # new, assigned, in_progress, etc. — idx in __table_args__
    status_reason = Column(String(100))  # Why in this status (e.g., "Awaiting user response")

    # Resolution
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(DateTime(timezone=True))
    resolution = Column(Text)  # Resolution notes
    resolution_reason = Column(String(100))  # fixed, workaround, duplicate, user_error, etc.
    close_notes = Column(Text)
    closed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    closed_at = Column(DateTime(timezone=True))

    # SLA Fields
    sla_target_respond = Column(DateTime(timezone=True))  # When response is due
    sla_target_resolve = Column(DateTime(timezone=True))  # When resolution is due
    sla_breach = Column(Boolean, default=False)
    response_time_minutes = Column(Integer)  # Actual response time
    resolution_time_minutes = Column(Integer)  # Actual resolution time

    # Audit & Tracking
    last_modified_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    last_modified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Additional Details (Class-specific fields can go here or in JSONB)
    additional_comments = Column(Text)  # Legacy work notes field
    work_notes = Column(JSON)  # Structured internal work notes (array of {author, date, comment})
    comments = Column(JSON)  # Structured public comments (array of {author, date, comment})
    root_cause = Column(Text)  # For incidents/problems
    workaround = Column(Text)  # Temporary workaround
    affected_services = Column(JSON)  # List of affected services
    affected_users_count = Column(Integer, default=1)

    # External References
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))  # Parent ticket (e.g., Problem -> Incidents)
    related_task_id = Column(UUID(as_uuid=True))  # Related ticket
    external_ticket_id = Column(String(100))  # Reference to external system

    # Custom Fields (Extensibility)
    custom_fields = Column(JSON)  # Any additional custom data

    # Contact Information
    contact_type = Column(String(50), default="email")  # email, phone, walk-in, portal

    # Relationships (lazy="select" — use selectinload() in queries for eager loading)
    tenant = relationship("Tenant", back_populates="tasks")
    company = relationship("Company", foreign_keys=[company_id])
    caller_company = relationship("Company", foreign_keys=[caller_company_id])
    affected_user_company = relationship("Company", foreign_keys=[affected_user_company_id])

    opened_by = relationship("User", foreign_keys=[opened_by_id])
    caller = relationship("User", foreign_keys=[caller_id])
    affected_user = relationship("User", foreign_keys=[affected_user_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    assignment_group = relationship("SupportGroup", foreign_keys=[assignment_group_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    closed_by = relationship("User", foreign_keys=[closed_by_id])
    last_modified_by = relationship("User", foreign_keys=[last_modified_by_id])

    # Self-referencing for parent/child tasks
    parent_task = relationship("Task", remote_side="Task.id", foreign_keys=[parent_task_id])

    # Attachments
    attachments = relationship("Attachment", back_populates="task", lazy="selectin")

    # Indexes for performance
    __table_args__ = (
        Index('idx_tasks_tenant_class', 'tenant_id', 'sys_class_name'),
        Index('idx_tasks_number', 'number'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_priority', 'priority'),
        Index('idx_tasks_assignment_group', 'assignment_group_id'),
        Index('idx_tasks_assigned_to', 'assigned_to_id'),
        Index('idx_tasks_company', 'company_id'),
        Index('idx_tasks_created', 'sys_created_on'),
    )

    def __repr__(self):
        return f"<Task {self.number}: {self.short_description}>"

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

    @staticmethod
    def generate_number(prefix: str, sequence: int) -> str:
        """
        Generate ticket number in format: PREFIX000000001

        Args:
            prefix: INC, REQ, CHG, PRB, TASK, RITM
            sequence: Sequential number

        Returns:
            Formatted ticket number (e.g., INC000000001)
        """
        return f"{prefix}{sequence:09d}"

    @staticmethod
    def get_prefix_for_class(sys_class_name: str) -> str:
        """Get the prefix for a given ticket class"""
        prefix_map = {
            "incident": "INC",
            "request": "REQ",
            "change": "CHG",
            "problem": "PRB",
            "task": "TASK",
            "approval": "APPR",
            "request_item": "RITM",
        }
        return prefix_map.get(sys_class_name, "TASK")
