// Metadata API response types — mirrors backend Pydantic schemas in sys_metadata.py

export interface SysDbObject {
  id: string;
  tenant_id?: string;
  name: string;
  label: string;
  plural_label?: string;
  super_class?: string;
  display_field?: string;
  number_prefix?: string;
  is_extendable: boolean;
  module?: string;
  icon?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysDictionary {
  id: string;
  tenant_id?: string;
  table_name: string;
  column_name: string;
  label: string;
  field_type: string; // string, text, integer, boolean, reference, choice, datetime, email, phone, url, json, uuid, password
  max_length?: number;
  is_mandatory: boolean;
  is_read_only: boolean;
  is_display: boolean;
  default_value?: string;
  reference_table?: string;
  reference_display_field?: string;
  hint?: string;
  description?: string;
  sort_order: number;
  sys_class_name?: string;
  is_system: boolean;
  column_exists: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysChoice {
  id: string;
  tenant_id?: string;
  table_name: string;
  field_name: string;
  value: string;
  label: string;
  sequence: number;
  sys_class_name?: string;
  dependent_field?: string;
  dependent_value?: string;
  color?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysUiView {
  id: string;
  tenant_id?: string;
  name: string;
  title: string;
  table_name: string;
  sys_class_name?: string;
  description?: string;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysUiElement {
  id: string;
  tenant_id?: string;
  section_id: string;
  field_name?: string;
  element_type: string; // field, separator, annotation
  sequence: number;
  column_index: number;
  annotation_text?: string;
  span: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysUiList {
  id: string;
  tenant_id?: string;
  view_id: string;
  field_name: string;
  sequence: number;
  sort_direction?: string;
  sort_priority?: number;
  width?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysRelationship {
  id: string;
  tenant_id?: string;
  name: string;
  parent_table: string;
  child_table: string;
  relationship_type: string; // one_to_many, many_to_many
  foreign_key_field?: string;
  join_table?: string;
  join_parent_field?: string;
  join_child_field?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SysUiRelatedList {
  id: string;
  tenant_id?: string;
  view_id: string;
  relationship_id: string;
  title: string;
  sequence: number;
  display_fields: string[];
  filter_condition?: Record<string, unknown>;
  max_rows: number;
  sys_class_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// Composite response types

export interface FormSectionWithElements {
  id: string;
  title: string;
  section_type: string; // fields, related_list, activity, attachments
  columns: number;
  sequence: number;
  is_expanded: boolean;
  position: string; // full, left, right
  sys_class_name?: string;
  elements: SysUiElement[];
}

export interface TableMetadataResponse {
  table: SysDbObject;
  fields: SysDictionary[];
  choices: SysChoice[];
  relationships: SysRelationship[];
}

export interface FormLayoutResponse {
  view: SysUiView;
  sections: FormSectionWithElements[];
  related_lists: SysUiRelatedList[];
}

export interface ListLayoutResponse {
  view: SysUiView;
  columns: SysUiList[];
}
