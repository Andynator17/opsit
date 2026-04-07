"""Support Group schemas"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class SupportGroupBase(BaseModel):
    """Base support group schema"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    email: Optional[str] = None
    group_type: str = Field(default="support")
    assignment_method: str = Field(default="manual")
    manager_id: Optional[UUID] = None


class SupportGroupCreate(SupportGroupBase):
    """Schema for creating support group"""
    member_ids: Optional[List[UUID]] = Field(default_factory=list)


class SupportGroupUpdate(BaseModel):
    """Schema for updating support group"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    email: Optional[str] = None
    group_type: Optional[str] = None
    assignment_method: Optional[str] = None
    manager_id: Optional[UUID] = None


class SupportGroupAddMembers(BaseModel):
    """Schema for adding members to group"""
    user_ids: List[UUID] = Field(..., min_items=1)


class SupportGroupMemberUpdate(BaseModel):
    """Schema for updating member details"""
    is_team_lead: bool = Field(..., description="Whether this user is a team lead")


class UserSummary(BaseModel):
    """User summary for group members"""
    id: UUID
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class MemberSummary(UserSummary):
    """Member summary with team lead flag"""
    is_team_lead: bool = False

    class Config:
        from_attributes = True


class SupportGroupResponse(BaseModel):
    """Support group response"""
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str]
    email: Optional[str]
    group_type: str
    assignment_method: str
    manager_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    manager: Optional[UserSummary] = None
    members: List[UserSummary] = []

    class Config:
        from_attributes = True


class SupportGroupListResponse(BaseModel):
    """List of support groups"""
    total: int
    groups: List[SupportGroupResponse]
