"""Role Schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=2, max_length=100, description="Role display name")
    code: str = Field(..., min_length=2, max_length=100, description="Role code (snake_case)")
    description: Optional[str] = None
    module: str = Field(..., description="Module name (incident, request, task, etc.)")
    level: str = Field(..., description="Permission level (read, read_create, agent, admin)")
    permissions: List[str] = Field(default_factory=list, description="List of permission strings")


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    is_system_role: bool = False


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    """Role response schema"""
    id: UUID
    tenant_id: UUID
    name: str
    code: str
    description: Optional[str]
    module: str
    level: str
    permissions: List[str]
    is_system_role: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """List of roles"""
    total: int
    roles: List[RoleResponse]
