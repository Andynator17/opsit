"""Permission Group Schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class UserSummary(BaseModel):
    """User summary for group members"""
    id: UUID
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class RoleSummary(BaseModel):
    """Role summary for permission groups"""
    id: UUID
    name: str
    code: str
    module: str
    level: str

    class Config:
        from_attributes = True


class PermissionGroupBase(BaseModel):
    """Base permission group schema"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class PermissionGroupCreate(PermissionGroupBase):
    """Schema for creating a permission group"""
    member_ids: List[UUID] = Field(default_factory=list, description="Initial members")
    role_ids: List[UUID] = Field(default_factory=list, description="Initial roles")


class PermissionGroupUpdate(BaseModel):
    """Schema for updating a permission group"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None


class PermissionGroupAddMembers(BaseModel):
    """Schema for adding members to permission group"""
    user_ids: List[UUID] = Field(..., min_items=1)


class PermissionGroupAddRoles(BaseModel):
    """Schema for adding roles to permission group"""
    role_ids: List[UUID] = Field(..., min_items=1)


class PermissionGroupResponse(BaseModel):
    """Permission group response"""
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    members: List[UserSummary] = []
    roles: List[RoleSummary] = []

    class Config:
        from_attributes = True


class PermissionGroupListResponse(BaseModel):
    """List of permission groups"""
    total: int
    permission_groups: List[PermissionGroupResponse]
