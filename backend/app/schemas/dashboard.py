"""Dashboard schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class DashboardStats(BaseModel):
    """Dashboard statistics for agents"""
    new_unassigned_incidents: int
    my_approvals_open: int
    my_requests_open: int
    sla_breach: int
    support_group_incidents: int
    support_group_changes: int
    support_group_tasks: int
    my_incidents: int
    my_changes: int
    my_tasks: int


class TicketSummary(BaseModel):
    """Ticket summary for overview console"""
    id: UUID
    ticket_number: str
    ticket_type: str  # incident, request, change, task
    title: str
    priority: str
    status: str
    assigned_to_name: Optional[str] = None
    support_group_name: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    sla_breach: bool = False

    class Config:
        from_attributes = True


class OverviewConsoleResponse(BaseModel):
    """Overview console with tickets and stats"""
    total: int
    tickets: List[TicketSummary]
