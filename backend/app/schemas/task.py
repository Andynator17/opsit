"""
Task schemas - Pydantic models for Task API (ServiceNow pattern)
Supports all ticket types: Incident, Request, Change, Problem, Task, Request Item
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Contact Types
CONTACT_TYPES = ["email", "phone", "walk_in", "web", "portal", "chat"]

# Ticket Classes
TICKET_CLASSES = ["incident", "request", "change", "problem", "task", "approval", "request_item"]

# Status values per class
STATUS_MAP = {
    "incident": ["new", "assigned", "in_progress", "pending", "resolved", "closed", "cancelled"],
    "request": ["submitted", "pending_approval", "approved", "rejected", "in_progress", "fulfilled", "closed", "cancelled"],
    "change": ["draft", "assessment", "approval", "scheduled", "implementation", "review", "closed", "cancelled"],
    "problem": ["new", "investigation", "root_cause_analysis", "resolved", "closed"],
    "task": ["pending", "open", "work_in_progress", "complete", "closed"],
    "approval": ["pending", "approved", "rejected", "cancelled"],
    "request_item": ["pending", "open", "work_in_progress", "complete", "closed"],
}


class TaskBase(BaseModel):
    """Base schema for Task (common fields)"""
    short_description: str = Field(..., min_length=5, max_length=255, description="Title/Summary")
    description: Optional[str] = Field(None, description="Detailed description")

    # Categorization
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    channel: str = Field(default="web", description="web, phone, email, walk_in, portal, chat")

    # Priority Matrix (ITIL)
    urgency: str = Field(..., description="low, medium, high, critical")
    impact: str = Field(..., description="low, medium, high, critical")

    # User fields
    caller_id: Optional[UUID] = Field(None, description="Person who reported")
    affected_user_id: Optional[UUID] = Field(None, description="User affected by issue")

    # Assignment
    assignment_group_id: Optional[UUID] = Field(None, description="Support group")
    assigned_to_id: Optional[UUID] = Field(None, description="Assigned user")

    # Custom fields
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator('urgency', 'impact')
    def validate_priority_values(cls, v):
        if v not in ['low', 'medium', 'high', 'critical']:
            raise ValueError('Must be one of: low, medium, high, critical')
        return v

    @field_validator('channel')
    def validate_channel(cls, v):
        if v not in CONTACT_TYPES:
            raise ValueError(f"Contact type must be one of: {', '.join(CONTACT_TYPES)}")
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    sys_class_name: str = Field(..., description="incident, request, change, problem, task, request_item")
    company_id: UUID = Field(..., description="Company creating the task")
    opened_by_id: Optional[UUID] = Field(None, description="User opening (auto-filled if not provided)")

    @field_validator('sys_class_name')
    def validate_class(cls, v):
        if v not in TICKET_CLASSES:
            raise ValueError(f"Class must be one of: {', '.join(TICKET_CLASSES)}")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating a task (partial updates allowed)"""
    short_description: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    channel: Optional[str] = None
    contact_type: Optional[str] = None
    urgency: Optional[str] = None
    impact: Optional[str] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    assignment_group_id: Optional[UUID] = None
    caller_id: Optional[UUID] = None
    affected_user_id: Optional[UUID] = None
    resolution: Optional[str] = None
    resolution_reason: Optional[str] = None
    root_cause: Optional[str] = None
    workaround: Optional[str] = None
    work_notes: Optional[List[Dict[str, Any]]] = Field(None, description="Internal work notes")
    comments: Optional[List[Dict[str, Any]]] = Field(None, description="Public comments")
    custom_fields: Optional[Dict[str, Any]] = None


class TaskAssign(BaseModel):
    """Schema for assigning a task"""
    assigned_to_id: Optional[UUID] = None
    assignment_group_id: Optional[UUID] = None


class TaskResolve(BaseModel):
    """Schema for resolving a task"""
    resolution_reason: str = Field(..., description="fixed, workaround, duplicate, user_error, etc.")
    resolution: str = Field(..., min_length=10, description="Resolution notes")
    root_cause: Optional[str] = Field(None, description="What caused this (for incidents/problems)")
    workaround: Optional[str] = Field(None, description="Temporary workaround")


class TaskClose(BaseModel):
    """Schema for closing a task"""
    close_notes: Optional[str] = Field(None, description="Final closure notes")


# Summary schemas for relationships
class UserSummary(BaseModel):
    """Summary of user info"""
    id: UUID
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class CompanySummary(BaseModel):
    """Summary of company info"""
    id: UUID
    name: str
    company_code: str

    class Config:
        from_attributes = True


class SupportGroupSummary(BaseModel):
    """Summary of support group info"""
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Full task response schema"""
    id: UUID
    sys_id: UUID
    tenant_id: UUID
    company_id: UUID
    number: str
    sys_class_name: str

    # Basic info
    short_description: str
    description: Optional[str]

    # Priority
    urgency: str
    impact: str
    priority: str

    # Status
    status: str
    status_reason: Optional[str]

    # Assignment
    assigned_to_id: Optional[UUID]
    assignment_group_id: Optional[UUID]
    reassignment_count: int

    # Users (ITIL distinction)
    opened_by_id: UUID
    caller_id: Optional[UUID]
    affected_user_id: Optional[UUID]

    # Categorization
    category: Optional[str]
    subcategory: Optional[str]
    channel: str

    # Resolution
    resolved_by_id: Optional[UUID]
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    resolution_reason: Optional[str]
    closed_by_id: Optional[UUID]
    closed_at: Optional[datetime]
    close_notes: Optional[str]

    # SLA
    sla_target_respond: Optional[datetime]
    sla_target_resolve: Optional[datetime]
    sla_breach: bool

    # Additional details
    root_cause: Optional[str]
    workaround: Optional[str]
    work_notes: Optional[List[Dict[str, Any]]]
    comments: Optional[List[Dict[str, Any]]]
    affected_services: Optional[List[str]]
    affected_users_count: Optional[int]

    # References
    parent_task_id: Optional[UUID]
    related_task_id: Optional[UUID]
    external_ticket_id: Optional[str]

    # Custom fields
    custom_fields: Optional[Dict[str, Any]]

    # Audit
    sys_created_on: datetime
    sys_updated_on: datetime
    last_modified_by_id: Optional[UUID]
    is_active: bool

    # Relationships (optional - only included when joined)
    opened_by: Optional[UserSummary] = None
    caller: Optional[UserSummary] = None
    affected_user: Optional[UserSummary] = None
    assigned_to: Optional[UserSummary] = None
    assignment_group: Optional[SupportGroupSummary] = None
    resolved_by: Optional[UserSummary] = None
    closed_by: Optional[UserSummary] = None
    company: Optional[CompanySummary] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Paginated list of tasks"""
    total: int
    tasks: List[TaskResponse]
    page: int
    page_size: int
