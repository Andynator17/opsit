"""Location schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class LocationCreate(BaseModel):
    """Schema for creating a location"""
    company_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class LocationUpdate(BaseModel):
    """Schema for updating a location"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_id: Optional[UUID] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class LocationCompanySummary(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)


class LocationResponse(BaseModel):
    """Location response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    company_id: UUID
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    company: Optional[LocationCompanySummary] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class LocationListResponse(BaseModel):
    """Response for listing locations"""
    total: int
    locations: List[LocationResponse]
