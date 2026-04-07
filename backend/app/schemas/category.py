"""Category schemas"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    category_type: str = Field(..., description="incident, request, knowledge_base, general")
    parent_category_id: Optional[UUID] = None
    level: int = Field(default=1, ge=1, le=3)
    sort_order: int = Field(default=0)
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating category"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseModel):
    """Category response"""
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str]
    category_type: str
    parent_category_id: Optional[UUID]
    level: int
    sort_order: int
    icon: Optional[str]
    color: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """List of categories"""
    total: int
    categories: List[CategoryResponse]
