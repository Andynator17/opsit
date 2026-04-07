"""Category model - Hierarchical categories for tickets and KB articles"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModelMixin


class Category(Base, BaseModelMixin):
    """Category model - Hierarchical categorization"""

    __tablename__ = "categories"

    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Category Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_type = Column(String(50), nullable=False, index=True)  # incident, request, knowledge_base, general

    # Hierarchy
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))  # For subcategories
    level = Column(Integer, nullable=False, default=1)  # 1=Category, 2=Subcategory, 3=Item
    sort_order = Column(Integer, default=0)  # For custom ordering

    # Icon/Color (for UI)
    icon = Column(String(50))  # Icon name (e.g., 'laptop', 'network', 'user')
    color = Column(String(20))  # Hex color code

    # Relationships
    parent = relationship("Category", remote_side="Category.id", backref="children")

    def __repr__(self):
        return f"<Category {self.name} ({self.category_type})>"
