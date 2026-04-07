"""Department schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class DepartmentCreate(BaseModel):
    """Schema for creating a department"""
    company_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    manager_id: Optional[UUID] = None
    parent_department_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    """Schema for updating a department"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    company_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    parent_department_id: Optional[UUID] = None


class ManagerSummary(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class CompanySummary(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)


class DepartmentResponse(BaseModel):
    """Department response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    company_id: UUID
    name: str
    description: Optional[str] = None
    manager_id: Optional[UUID] = None
    parent_department_id: Optional[UUID] = None
    manager: Optional[ManagerSummary] = None
    company: Optional[CompanySummary] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class DepartmentListResponse(BaseModel):
    """Response for listing departments"""
    total: int
    departments: List[DepartmentResponse]
