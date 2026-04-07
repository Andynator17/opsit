"""Portal schemas"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PortalCreate(BaseModel):
    """Schema for creating a portal"""
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9\-]+$")
    description: Optional[str] = None
    audience_type: str = Field(default="internal")
    company_id: Optional[UUID] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(default="#667eea", max_length=20)
    accent_color: Optional[str] = Field(default="#764ba2", max_length=20)
    welcome_title: Optional[str] = None
    welcome_message: Optional[str] = None
    enabled_modules: List[str] = Field(default_factory=lambda: ["tickets", "services", "knowledge_base", "profile"])
    visible_categories: List[str] = Field(default_factory=list)
    default_ticket_type: str = Field(default="incident")
    is_default: bool = False
    sort_order: int = 0


class PortalUpdate(BaseModel):
    """Schema for updating a portal"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=100, pattern=r"^[a-z0-9\-]+$")
    description: Optional[str] = None
    audience_type: Optional[str] = None
    company_id: Optional[UUID] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    welcome_title: Optional[str] = None
    welcome_message: Optional[str] = None
    enabled_modules: Optional[List[str]] = None
    visible_categories: Optional[List[str]] = None
    default_ticket_type: Optional[str] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None


class PortalResponse(BaseModel):
    """Full portal response (admin)"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    audience_type: str
    company_id: Optional[UUID] = None
    logo_url: Optional[str] = None
    primary_color: str
    accent_color: str
    welcome_title: Optional[str] = None
    welcome_message: Optional[str] = None
    enabled_modules: List[str] = []
    visible_categories: List[str] = []
    default_ticket_type: str
    is_default: bool
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class PortalPublicResponse(BaseModel):
    """Public portal response (end-user, branding only)"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str
    accent_color: str
    welcome_title: Optional[str] = None
    welcome_message: Optional[str] = None
    enabled_modules: List[str] = []
    default_ticket_type: str


class PortalListResponse(BaseModel):
    """Response for portal list"""
    items: List[PortalResponse]
    total: int


class PortalMyStatsResponse(BaseModel):
    """Portal stats for current user"""
    open_incidents: int = 0
    open_requests: int = 0
    pending_approvals: int = 0
    resolved_last_30_days: int = 0
    total_tickets: int = 0
