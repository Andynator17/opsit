"""Request schemas - Request/Response validation"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Enums
URGENCY_LEVELS = ["low", "medium", "high", "critical"]
PRIORITY_LEVELS = ["low", "medium", "high", "critical"]
STATUS_CHOICES = ["submitted", "pending_approval", "approved", "rejected", "in_progress", "fulfilled", "closed", "cancelled"]
CONTACT_TYPES = ["phone", "email", "portal", "chat", "walk-in"]


class RequestBase(BaseModel):
    """Base request schema"""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    category: str = Field(..., max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    catalog_item: Optional[str] = Field(None, max_length=100)
    urgency: str = Field(default="medium")
    contact_type: str = Field(default="portal")
    business_justification: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        if v not in URGENCY_LEVELS:
            raise ValueError(f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}")
        return v

    @field_validator("contact_type")
    @classmethod
    def validate_contact_type(cls, v: str) -> str:
        if v not in CONTACT_TYPES:
            raise ValueError(f"Contact type must be one of: {', '.join(CONTACT_TYPES)}")
        return v


class RequestCreate(RequestBase):
    """Schema for creating a new request"""
    company_id: UUID
    requested_by_id: Optional[UUID] = None  # Auto-filled if not provided
    requested_for_id: Optional[UUID] = None  # If requesting for someone else
    requires_approval: bool = False


class RequestUpdate(BaseModel):
    """Schema for updating a request"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    catalog_item: Optional[str] = None
    urgency: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    assigned_group_id: Optional[UUID] = None
    business_justification: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in URGENCY_LEVELS:
            raise ValueError(f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in STATUS_CHOICES:
            raise ValueError(f"Status must be one of: {', '.join(STATUS_CHOICES)}")
        return v


class RequestApprove(BaseModel):
    """Schema for approving a request"""
    approval_notes: Optional[str] = None


class RequestReject(BaseModel):
    """Schema for rejecting a request"""
    rejection_reason: str = Field(..., min_length=10)


class RequestAssign(BaseModel):
    """Schema for assigning a request"""
    assigned_to_id: Optional[UUID] = None
    assigned_group_id: Optional[UUID] = None


class RequestFulfill(BaseModel):
    """Schema for fulfilling a request"""
    fulfillment_notes: str = Field(..., min_length=10)


class RequestClose(BaseModel):
    """Schema for closing a request"""
    closure_notes: Optional[str] = None


class UserSummary(BaseModel):
    """User summary"""
    id: UUID
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class CompanySummary(BaseModel):
    """Company summary"""
    id: UUID
    name: str
    company_code: str

    class Config:
        from_attributes = True


class RequestResponse(BaseModel):
    """Full request response"""
    id: UUID
    tenant_id: UUID
    company_id: UUID
    request_number: str
    title: str
    description: str
    category: str
    subcategory: Optional[str]
    catalog_item: Optional[str]
    urgency: str
    priority: str
    status: str
    status_reason: Optional[str]

    # Requester
    requested_by_id: UUID
    requested_for_id: Optional[UUID]
    requested_date: datetime
    contact_type: str

    # Approval
    requires_approval: bool
    approved_by_id: Optional[UUID]
    approved_date: Optional[datetime]
    approval_notes: Optional[str]
    rejection_reason: Optional[str]

    # Assignment
    assigned_to_id: Optional[UUID]
    assigned_group_id: Optional[UUID]

    # Fulfillment
    fulfilled_by_id: Optional[UUID]
    fulfilled_date: Optional[datetime]
    fulfillment_notes: Optional[str]

    # Closure
    closed_by_id: Optional[UUID]
    closed_date: Optional[datetime]
    closure_notes: Optional[str]

    # SLA
    sla_target_fulfill: Optional[datetime]
    sla_breach: str
    fulfillment_time_minutes: Optional[int]

    # Additional
    business_justification: Optional[str]
    cost_center: Optional[str]
    estimated_cost: Optional[str]
    quantity: int
    custom_fields: Optional[Dict[str, Any]]

    # Audit
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Relationships
    requested_by: Optional[UserSummary] = None
    requested_for: Optional[UserSummary] = None
    approved_by: Optional[UserSummary] = None
    assigned_to: Optional[UserSummary] = None
    fulfilled_by: Optional[UserSummary] = None
    closed_by: Optional[UserSummary] = None
    company: Optional[CompanySummary] = None

    class Config:
        from_attributes = True


class RequestListResponse(BaseModel):
    """Paginated list of requests"""
    total: int
    requests: List[RequestResponse]
    page: int
    page_size: int
