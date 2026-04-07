"""Schemas for ClientScript (Browser-Side UI Rules)"""
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ClientScriptCondition(BaseModel):
    field: str
    operator: str  # is_empty, is_not_empty, equals, not_equals, in, not_in, contains
    value: Any = None


class ClientScriptUIAction(BaseModel):
    type: str  # set_hidden, set_readonly, set_mandatory, set_value
    field: str
    value: Any = None


class ClientScriptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    table_name: str = Field(default="tasks", max_length=50)
    sys_class_name: Optional[str] = None
    event: str = Field(..., pattern="^(on_load|on_change|on_submit)$")
    trigger_field: Optional[str] = None
    execution_order: int = Field(default=100, ge=0, le=10000)
    condition_logic: str = Field(default="and", pattern="^(and|or)$")
    conditions: List[ClientScriptCondition] = Field(default_factory=list)
    ui_actions: List[ClientScriptUIAction] = Field(default_factory=list)
    is_active: bool = True


class ClientScriptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    table_name: Optional[str] = Field(None, max_length=50)
    sys_class_name: Optional[str] = None
    event: Optional[str] = Field(None, pattern="^(on_load|on_change|on_submit)$")
    trigger_field: Optional[str] = None
    execution_order: Optional[int] = Field(None, ge=0, le=10000)
    condition_logic: Optional[str] = Field(None, pattern="^(and|or)$")
    conditions: Optional[List[ClientScriptCondition]] = None
    ui_actions: Optional[List[ClientScriptUIAction]] = None
    is_active: Optional[bool] = None


class ClientScriptResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str] = None
    table_name: str
    sys_class_name: Optional[str] = None
    event: str
    trigger_field: Optional[str] = None
    execution_order: int
    condition_logic: str
    conditions: List[ClientScriptCondition]
    ui_actions: List[ClientScriptUIAction]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientScriptListResponse(BaseModel):
    total: int
    items: List[ClientScriptResponse]
    page: int
    page_size: int
