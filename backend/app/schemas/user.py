"""User schemas"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    email_secondary: Optional[str] = None
    employee_id: Optional[str] = None
    salutation: Optional[str] = None
    title: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    phone_secondary: Optional[str] = None
    mobile: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    user_type: str = "employee"
    language: str = "en"
    timezone: str = "UTC"


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)
    company_id: Optional[UUID] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    tenant_id: UUID
    primary_company_id: UUID
    user_type: str
    is_vip: bool
    is_support_agent: bool
    is_admin: bool
    department_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    is_active: bool
    avatar_url: Optional[str] = None
    locked_until: Optional[datetime] = None
    failed_login_attempts: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserUpdate(BaseModel):
    """Schema for updating user"""
    primary_company_id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    email_secondary: Optional[str] = None
    employee_id: Optional[str] = None
    salutation: Optional[str] = None
    title: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    phone_secondary: Optional[str] = None
    mobile: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    user_type: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_vip: Optional[bool] = None
    is_support_agent: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
