"""Tenant schemas"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TenantResponse(BaseModel):
    """Tenant response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    subdomain: str
    status: str
    plan: str
    max_users: int
    created_at: datetime
