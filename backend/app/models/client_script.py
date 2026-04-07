"""ClientScript model — declarative browser-side UI rules (like ServiceNow Client Scripts)"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class ClientScript(Base, BaseModelMixin):
    """
    Declarative client-side rule that controls form UI behavior.

    Rules are JSON-based (no eval/exec). Conditions are evaluated in the browser;
    if conditions pass, UI actions (hide/readonly/mandatory/set_value) are applied.
    """

    __tablename__ = "client_scripts"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Scope
    table_name = Column(String(50), nullable=False, default="tasks")
    sys_class_name = Column(String(50), nullable=True)  # NULL = all ticket types

    # Event: on_load, on_change, on_submit
    event = Column(String(30), nullable=False)

    # For on_change: which field triggers re-evaluation (NULL = any field change)
    trigger_field = Column(String(100), nullable=True)

    # Lower number = runs first
    execution_order = Column(Integer, nullable=False, default=100)

    # Condition logic: "and" = all must match, "or" = any must match
    condition_logic = Column(String(10), nullable=False, default="and")

    # Rule definition (JSON arrays)
    conditions = Column(JSON, nullable=False, default=list)
    ui_actions = Column(JSON, nullable=False, default=list)

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_client_scripts_tenant_table_event", "tenant_id", "table_name", "event"),
    )

    def __repr__(self):
        return f"<ClientScript {self.name} [{self.event}]>"
