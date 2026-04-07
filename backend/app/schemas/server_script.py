"""Schemas for ServerScript (Business Rules)"""
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ServerScriptCondition(BaseModel):
    field: str
    operator: str  # is_empty, is_not_empty, equals, not_equals, in, not_in, contains, changed, changed_to, changed_from
    value: Any = None


class ServerScriptAction(BaseModel):
    type: str  # set_value, set_value_from_query
    field: str
    value: Any = None
    # For set_value_from_query
    query_model: Optional[str] = None
    query_filters: Optional[dict] = None
    query_field: Optional[str] = None


class ServerScriptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    table_name: str = Field(default="tasks", max_length=50)
    sys_class_name: Optional[str] = None
    timing: str = Field(..., pattern="^(before_create|after_create|before_update|after_update|before_submit|after_submit)$")
    execution_order: int = Field(default=100, ge=0, le=10000)
    condition_logic: str = Field(default="and", pattern="^(and|or)$")
    conditions: List[ServerScriptCondition] = Field(default_factory=list)
    actions: List[ServerScriptAction] = Field(default_factory=list)
    is_active: bool = True


class ServerScriptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    table_name: Optional[str] = Field(None, max_length=50)
    sys_class_name: Optional[str] = None
    timing: Optional[str] = Field(None, pattern="^(before_create|after_create|before_update|after_update|before_submit|after_submit)$")
    execution_order: Optional[int] = Field(None, ge=0, le=10000)
    condition_logic: Optional[str] = Field(None, pattern="^(and|or)$")
    conditions: Optional[List[ServerScriptCondition]] = None
    actions: Optional[List[ServerScriptAction]] = None
    is_active: Optional[bool] = None


class ServerScriptResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str] = None
    table_name: str
    sys_class_name: Optional[str] = None
    timing: str
    execution_order: int
    condition_logic: str
    conditions: List[ServerScriptCondition]
    actions: List[ServerScriptAction]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServerScriptListResponse(BaseModel):
    total: int
    items: List[ServerScriptResponse]
    page: int
    page_size: int
