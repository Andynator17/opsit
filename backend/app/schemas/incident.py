"""Incident schemas - Request/Response validation"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Enums for validation
URGENCY_LEVELS = ["low", "medium", "high", "critical"]
IMPACT_LEVELS = ["low", "medium", "high", "critical"]
PRIORITY_LEVELS = ["low", "medium", "high", "critical"]
STATUS_CHOICES = ["new", "assigned", "in_progress", "pending", "resolved", "closed", "cancelled"]
CONTACT_TYPES = ["phone", "email", "portal", "chat", "walk-in"]


class IncidentBase(BaseModel):
    """Base incident schema"""
    title: str = Field(..., min_length=5, max_length=255, description="Incident title")
    description: str = Field(..., min_length=10, description="Detailed description")
    category: str = Field(..., max_length=100, description="Main category")
    subcategory: Optional[str] = Field(None, max_length=100)
    item: Optional[str] = Field(None, max_length=100)
    urgency: str = Field(default="medium", description="Urgency level")
    impact: str = Field(default="medium", description="Impact level")
    contact_type: str = Field(default="portal")
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        if v not in URGENCY_LEVELS:
            raise ValueError(f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}")
        return v

    @field_validator("impact")
    @classmethod
    def validate_impact(cls, v: str) -> str:
        if v not in IMPACT_LEVELS:
            raise ValueError(f"Impact must be one of: {', '.join(IMPACT_LEVELS)}")
        return v

    @field_validator("contact_type")
    @classmethod
    def validate_contact_type(cls, v: str) -> str:
        if v not in CONTACT_TYPES:
            raise ValueError(f"Contact type must be one of: {', '.join(CONTACT_TYPES)}")
        return v


class IncidentCreate(IncidentBase):
    """Schema for creating a new incident"""
    company_id: UUID = Field(..., description="Company reporting the incident")
    reported_by_id: Optional[UUID] = Field(None, description="User reporting (auto-filled if not provided)")
    opened_by_id: Optional[UUID] = Field(None, description="User who opened the ticket (auto-filled if not provided)")
    caller_id: Optional[UUID] = Field(None, description="Person who reported the issue")
    affected_user_id: Optional[UUID] = Field(None, description="User affected by the incident")
    assigned_group_id: Optional[UUID] = Field(None, description="Support group to assign to")


class IncidentUpdate(BaseModel):
    """Schema for updating an incident (partial updates allowed)"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    item: Optional[str] = None
    urgency: Optional[str] = None
    impact: Optional[str] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    assigned_group_id: Optional[UUID] = None
    caller_id: Optional[UUID] = None
    affected_user_id: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    resolution_code: Optional[str] = None
    root_cause: Optional[str] = None
    workaround: Optional[str] = None
    affected_services: Optional[List[str]] = None
    affected_users_count: Optional[int] = Field(None, ge=1)
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in URGENCY_LEVELS:
            raise ValueError(f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}")
        return v

    @field_validator("impact")
    @classmethod
    def validate_impact(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in IMPACT_LEVELS:
            raise ValueError(f"Impact must be one of: {', '.join(IMPACT_LEVELS)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in STATUS_CHOICES:
            raise ValueError(f"Status must be one of: {', '.join(STATUS_CHOICES)}")
        return v


class IncidentAssign(BaseModel):
    """Schema for assigning an incident"""
    assigned_to_id: Optional[UUID] = Field(None, description="Assign to specific user")
    assigned_group_id: Optional[UUID] = Field(None, description="Assign to support group")


class IncidentResolve(BaseModel):
    """Schema for resolving an incident"""
    resolution_notes: str = Field(..., min_length=10, description="Resolution details")
    resolution_code: str = Field(..., description="Resolution code")
    root_cause: Optional[str] = None


class IncidentClose(BaseModel):
    """Schema for closing an incident"""
    closure_notes: Optional[str] = None


class UserSummary(BaseModel):
    """Summary of user info for relationships"""
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


class IncidentResponse(BaseModel):
    """Full incident response schema"""
    id: UUID
    tenant_id: UUID
    company_id: UUID
    incident_number: str
    title: str
    description: str
    category: str
    subcategory: Optional[str]
    item: Optional[str]
    urgency: str
    impact: str
    priority: str
    status: str
    status_reason: Optional[str]

    # Assignment
    assigned_to_id: Optional[UUID]
    assigned_group_id: Optional[UUID]

    # Reporter & Affected Users (ITIL distinction)
    opened_by_id: UUID
    caller_id: Optional[UUID]
    affected_user_id: Optional[UUID]
    reported_by_id: UUID  # Deprecated: use opened_by_id
    reported_date: datetime
    contact_type: str

    # Resolution
    resolved_by_id: Optional[UUID]
    resolved_date: Optional[datetime]
    resolution_notes: Optional[str]
    resolution_code: Optional[str]

    # Closure
    closed_by_id: Optional[UUID]
    closed_date: Optional[datetime]

    # SLA
    sla_target_resolve: Optional[datetime]
    sla_target_respond: Optional[datetime]
    sla_breach: str
    response_time_minutes: Optional[int]
    resolution_time_minutes: Optional[int]

    # Additional
    root_cause: Optional[str]
    workaround: Optional[str]
    affected_services: Optional[Dict[str, Any]]
    affected_users_count: int
    custom_fields: Optional[Dict[str, Any]]

    # Audit
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Relationships (optional - only included when joined)
    opened_by: Optional[UserSummary] = None
    caller: Optional[UserSummary] = None
    affected_user: Optional[UserSummary] = None
    reported_by: Optional[UserSummary] = None  # Deprecated: use opened_by
    assigned_to: Optional[UserSummary] = None
    assigned_group: Optional[SupportGroupSummary] = None
    resolved_by: Optional[UserSummary] = None
    closed_by: Optional[UserSummary] = None
    company: Optional[CompanySummary] = None

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """Paginated list of incidents"""
    total: int
    incidents: List[IncidentResponse]
    page: int
    page_size: int
