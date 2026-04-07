"""Company schemas"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class CompanyBase(BaseModel):
    """Base company schema"""
    name: str = Field(..., min_length=2, max_length=255)
    legal_name: Optional[str] = None
    company_code: str = Field(..., min_length=2, max_length=50)
    company_type: str = Field(default="internal")
    parent_company_id: Optional[UUID] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    is_main_it_company: bool = False
    status: Optional[str] = "active"


class CompanyCreate(CompanyBase):
    """Schema for creating company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating company"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    legal_name: Optional[str] = None
    company_type: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    is_main_it_company: Optional[bool] = None
    status: Optional[str] = None


class CompanyResponse(BaseModel):
    """Company response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    company_code: Optional[str]
    company_type: str
    status: str
    is_main_it_company: bool = False
    primary_email: Optional[str]
    city: Optional[str]
    country: Optional[str]
    created_at: datetime
