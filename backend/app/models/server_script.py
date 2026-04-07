"""ServerScript model — declarative business rules (like ServiceNow Business Rules)"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class ServerScript(Base, BaseModelMixin):
    """
    Declarative server-side rule that runs before/after task create/update.

    Rules are JSON-based (no eval/exec). Conditions are evaluated with AND/OR logic;
    if conditions pass, actions are executed in order.
    """

    __tablename__ = "server_scripts"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Scope
    table_name = Column(String(50), nullable=False, default="tasks")
    sys_class_name = Column(String(50), nullable=True)  # NULL = all ticket types

    # Timing: before_create, after_create, before_update, after_update
    timing = Column(String(30), nullable=False)

    # Lower number = runs first
    execution_order = Column(Integer, nullable=False, default=100)

    # Condition logic: "and" = all must match, "or" = any must match
    condition_logic = Column(String(10), nullable=False, default="and")

    # Rule definition (JSON arrays)
    conditions = Column(JSON, nullable=False, default=list)
    actions = Column(JSON, nullable=False, default=list)

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_server_scripts_tenant_table_timing", "tenant_id", "table_name", "timing"),
    )

    def __repr__(self):
        return f"<ServerScript {self.name} [{self.timing}]>"
