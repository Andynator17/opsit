"""
System Metadata schemas - Pydantic v2 models for the metadata-driven platform layer.

Covers all 9 metadata tables:
  SysDbObject, SysDictionary, SysChoice, SysUiView, SysUiSection,
  SysUiElement, SysUiList, SysRelationship, SysUiRelatedList

Plus composite response schemas for table metadata, form layout, and list layout.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


# ---------------------------------------------------------------------------
#  1. SysDbObject  (table registry)
# ---------------------------------------------------------------------------

class SysDbObjectCreate(BaseModel):
    """Create a table registration."""
    tenant_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255, description="Internal table name")
    label: str = Field(..., min_length=1, max_length=255, description="Singular display label")
    plural_label: Optional[str] = Field(None, max_length=255)
    super_class: Optional[str] = Field(None, max_length=255, description="Parent table name")
    display_field: Optional[str] = Field(None, max_length=255)
    number_prefix: Optional[str] = Field(None, max_length=20, description="Auto-number prefix, e.g. INC")
    is_extendable: bool = True
    module: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class SysDbObjectUpdate(BaseModel):
    """Update a table registration (partial)."""
    tenant_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    plural_label: Optional[str] = None
    super_class: Optional[str] = None
    display_field: Optional[str] = None
    number_prefix: Optional[str] = None
    is_extendable: Optional[bool] = None
    module: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class SysDbObjectResponse(BaseModel):
    """Table registration response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    name: str
    label: str
    plural_label: Optional[str] = None
    super_class: Optional[str] = None
    display_field: Optional[str] = None
    number_prefix: Optional[str] = None
    is_extendable: bool
    module: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class SysDbObjectListResponse(BaseModel):
    """Paginated list of table registrations."""
    total: int
    items: list[SysDbObjectResponse]
    page: int
    page_size: int


# ---------------------------------------------------------------------------
#  2. SysDictionary  (field dictionary)
# ---------------------------------------------------------------------------

class SysDictionaryCreate(BaseModel):
    """Create a field dictionary entry."""
    tenant_id: Optional[UUID] = None
    table_name: str = Field(..., min_length=1, max_length=255)
    column_name: str = Field(..., min_length=1, max_length=255)
    label: str = Field(..., min_length=1, max_length=255)
    field_type: str = Field(..., max_length=50, description="string, integer, boolean, reference, choice, etc.")
    max_length: Optional[int] = None
    is_mandatory: bool = False
    is_read_only: bool = False
    is_display: bool = False
    default_value: Optional[str] = None
    reference_table: Optional[str] = Field(None, max_length=255)
    reference_display_field: Optional[str] = Field(None, max_length=255)
    hint: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 100
    sys_class_name: Optional[str] = Field(None, max_length=255)
    is_system: bool = False
    column_exists: bool = True


class SysDictionaryUpdate(BaseModel):
    """Update a field dictionary entry (partial)."""
    tenant_id: Optional[UUID] = None
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    label: Optional[str] = None
    field_type: Optional[str] = None
    max_length: Optional[int] = None
    is_mandatory: Optional[bool] = None
    is_read_only: Optional[bool] = None
    is_display: Optional[bool] = None
    default_value: Optional[str] = None
    reference_table: Optional[str] = None
    reference_display_field: Optional[str] = None
    hint: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    sys_class_name: Optional[str] = None
    is_system: Optional[bool] = None
    column_exists: Optional[bool] = None


class SysDictionaryResponse(BaseModel):
    """Field dictionary response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    table_name: str
    column_name: str
    label: str
    field_type: str
    max_length: Optional[int] = None
    is_mandatory: bool
    is_read_only: bool
    is_display: bool
    default_value: Optional[str] = None
    reference_table: Optional[str] = None
    reference_display_field: Optional[str] = None
    hint: Optional[str] = None
    description: Optional[str] = None
    sort_order: int
    sys_class_name: Optional[str] = None
    is_system: bool
    column_exists: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class SysDictionaryListResponse(BaseModel):
    """Paginated list of dictionary entries."""
    total: int
    items: list[SysDictionaryResponse]
    page: int
    page_size: int


# ---------------------------------------------------------------------------
#  3. SysChoice  (choice / drop-down values)
# ---------------------------------------------------------------------------

class SysChoiceCreate(BaseModel):
    """Create a choice value."""
    tenant_id: Optional[UUID] = None
    table_name: str = Field(..., min_length=1, max_length=255)
    field_name: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1, max_length=255)
    label: str = Field(..., min_length=1, max_length=255)
    sequence: int = 100
    sys_class_name: Optional[str] = Field(None, max_length=255)
    dependent_field: Optional[str] = Field(None, max_length=255)
    dependent_value: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=50)


class SysChoiceUpdate(BaseModel):
    """Update a choice value (partial)."""
    tenant_id: Optional[UUID] = None
    table_name: Optional[str] = None
    field_name: Optional[str] = None
    value: Optional[str] = None
    label: Optional[str] = None
    sequence: Optional[int] = None
    sys_class_name: Optional[str] = None
    dependent_field: Optional[str] = None
    dependent_value: Optional[str] = None
    color: Optional[str] = None


class SysChoiceResponse(BaseModel):
    """Choice value response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    table_name: str
    field_name: str
    value: str
    label: str
    sequence: int
    sys_class_name: Optional[str] = None
    dependent_field: Optional[str] = None
    dependent_value: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class SysChoiceListResponse(BaseModel):
    """Paginated list of choice values."""
    total: int
    items: list[SysChoiceResponse]
    page: int
    page_size: int


# ---------------------------------------------------------------------------
#  4. SysUiView  (views)
# ---------------------------------------------------------------------------

class SysUiViewCreate(BaseModel):
    """Create a UI view."""
    tenant_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    table_name: str = Field(..., min_length=1, max_length=255)
    sys_class_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_default: bool = False


class SysUiViewUpdate(BaseModel):
    """Update a UI view (partial)."""
    tenant_id: Optional[UUID] = None
    name: Optional[str] = None
    title: Optional[str] = None
    table_name: Optional[str] = None
    sys_class_name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class SysUiViewResponse(BaseModel):
    """UI view response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    name: str
    title: str
    table_name: str
    sys_class_name: Optional[str] = None
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
#  5. SysUiSection  (form sections)
# ---------------------------------------------------------------------------

class SysUiSectionCreate(BaseModel):
    """Create a form section."""
    tenant_id: Optional[UUID] = None
    view_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    section_type: str = Field(default="fields", max_length=50)
    columns: int = Field(default=2, ge=1, le=4)
    sequence: int = 100
    is_expanded: bool = True
    position: str = Field(default="full", max_length=50)
    sys_class_name: Optional[str] = Field(None, max_length=255)


class SysUiSectionUpdate(BaseModel):
    """Update a form section (partial)."""
    tenant_id: Optional[UUID] = None
    view_id: Optional[UUID] = None
    title: Optional[str] = None
    section_type: Optional[str] = None
    columns: Optional[int] = Field(None, ge=1, le=4)
    sequence: Optional[int] = None
    is_expanded: Optional[bool] = None
    position: Optional[str] = None
    sys_class_name: Optional[str] = None


class SysUiSectionResponse(BaseModel):
    """Form section response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    view_id: UUID
    title: str
    section_type: str
    columns: int
    sequence: int
    is_expanded: bool
    position: str
    sys_class_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
#  6. SysUiElement  (form elements within a section)
# ---------------------------------------------------------------------------

class SysUiElementCreate(BaseModel):
    """Create a form element."""
    tenant_id: Optional[UUID] = None
    section_id: UUID
    field_name: Optional[str] = Field(None, max_length=255)
    element_type: str = Field(default="field", max_length=50)
    sequence: int = 100
    column_index: int = Field(default=1, ge=1)
    annotation_text: Optional[str] = None
    span: int = Field(default=1, ge=1)


class SysUiElementUpdate(BaseModel):
    """Update a form element (partial)."""
    tenant_id: Optional[UUID] = None
    section_id: Optional[UUID] = None
    field_name: Optional[str] = None
    element_type: Optional[str] = None
    sequence: Optional[int] = None
    column_index: Optional[int] = Field(None, ge=1)
    annotation_text: Optional[str] = None
    span: Optional[int] = Field(None, ge=1)


class SysUiElementResponse(BaseModel):
    """Form element response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    section_id: UUID
    field_name: Optional[str] = None
    element_type: str
    sequence: int
    column_index: int
    annotation_text: Optional[str] = None
    span: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
#  7. SysUiList  (list/table columns)
# ---------------------------------------------------------------------------

class SysUiListCreate(BaseModel):
    """Create a list column entry."""
    tenant_id: Optional[UUID] = None
    view_id: UUID
    field_name: str = Field(..., min_length=1, max_length=255)
    sequence: int = 100
    sort_direction: Optional[str] = Field(None, max_length=10, description="asc or desc")
    sort_priority: Optional[int] = None
    width: Optional[int] = None


class SysUiListUpdate(BaseModel):
    """Update a list column entry (partial)."""
    tenant_id: Optional[UUID] = None
    view_id: Optional[UUID] = None
    field_name: Optional[str] = None
    sequence: Optional[int] = None
    sort_direction: Optional[str] = None
    sort_priority: Optional[int] = None
    width: Optional[int] = None


class SysUiListResponse(BaseModel):
    """List column response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    view_id: UUID
    field_name: str
    sequence: int
    sort_direction: Optional[str] = None
    sort_priority: Optional[int] = None
    width: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
#  8. SysRelationship  (table relationships)
# ---------------------------------------------------------------------------

class SysRelationshipCreate(BaseModel):
    """Create a relationship definition."""
    tenant_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    parent_table: str = Field(..., min_length=1, max_length=255)
    child_table: str = Field(..., min_length=1, max_length=255)
    relationship_type: str = Field(..., max_length=50, description="one_to_many, many_to_many, one_to_one")
    foreign_key_field: Optional[str] = Field(None, max_length=255)
    join_table: Optional[str] = Field(None, max_length=255)
    join_parent_field: Optional[str] = Field(None, max_length=255)
    join_child_field: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class SysRelationshipUpdate(BaseModel):
    """Update a relationship definition (partial)."""
    tenant_id: Optional[UUID] = None
    name: Optional[str] = None
    parent_table: Optional[str] = None
    child_table: Optional[str] = None
    relationship_type: Optional[str] = None
    foreign_key_field: Optional[str] = None
    join_table: Optional[str] = None
    join_parent_field: Optional[str] = None
    join_child_field: Optional[str] = None
    description: Optional[str] = None


class SysRelationshipResponse(BaseModel):
    """Relationship definition response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    name: str
    parent_table: str
    child_table: str
    relationship_type: str
    foreign_key_field: Optional[str] = None
    join_table: Optional[str] = None
    join_parent_field: Optional[str] = None
    join_child_field: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class SysRelationshipListResponse(BaseModel):
    """Paginated list of relationships."""
    total: int
    items: list[SysRelationshipResponse]
    page: int
    page_size: int


# ---------------------------------------------------------------------------
#  9. SysUiRelatedList  (related lists on forms)
# ---------------------------------------------------------------------------

class SysUiRelatedListCreate(BaseModel):
    """Create a related list entry."""
    tenant_id: Optional[UUID] = None
    view_id: UUID
    relationship_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    sequence: int = 100
    display_fields: list[str] = Field(default_factory=list)
    filter_condition: Optional[dict[str, Any]] = None
    max_rows: int = Field(default=20, ge=1, le=500)
    sys_class_name: Optional[str] = Field(None, max_length=255)


class SysUiRelatedListUpdate(BaseModel):
    """Update a related list entry (partial)."""
    tenant_id: Optional[UUID] = None
    view_id: Optional[UUID] = None
    relationship_id: Optional[UUID] = None
    title: Optional[str] = None
    sequence: Optional[int] = None
    display_fields: Optional[list[str]] = None
    filter_condition: Optional[dict[str, Any]] = None
    max_rows: Optional[int] = Field(None, ge=1, le=500)
    sys_class_name: Optional[str] = None


class SysUiRelatedListResponse(BaseModel):
    """Related list response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: Optional[UUID] = None
    view_id: UUID
    relationship_id: UUID
    title: str
    sequence: int
    display_fields: list[str]
    filter_condition: Optional[dict[str, Any]] = None
    max_rows: int
    sys_class_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
#  Composite Response Schemas
# ---------------------------------------------------------------------------

class TableMetadataResponse(BaseModel):
    """
    Full metadata bundle for a single table.
    Returned by GET /api/v1/metadata/tables/{table_name}.
    """
    table: SysDbObjectResponse
    fields: list[SysDictionaryResponse]
    choices: list[SysChoiceResponse]
    relationships: list[SysRelationshipResponse]


class FormSectionWithElements(BaseModel):
    """A form section with its child elements inlined."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    section_type: str
    columns: int
    sequence: int
    is_expanded: bool
    position: str
    sys_class_name: Optional[str] = None
    elements: list[SysUiElementResponse] = Field(default_factory=list)


class FormLayoutResponse(BaseModel):
    """
    Complete form layout for a table + view.
    Returned by GET /api/v1/metadata/tables/{table_name}/form.
    """
    view: SysUiViewResponse
    sections: list[FormSectionWithElements]
    related_lists: list[SysUiRelatedListResponse]


class ListLayoutResponse(BaseModel):
    """
    List (table grid) layout for a table + view.
    Returned by GET /api/v1/metadata/tables/{table_name}/list.
    """
    view: SysUiViewResponse
    columns: list[SysUiListResponse]
