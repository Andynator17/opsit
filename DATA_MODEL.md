# OpsIT - Data Model

## Design Principles
1. **Extensible**: Easy to add new modules (CMDB, Asset, Service, HR)
2. **Inheritance**: Base classes for shared behavior
3. **Relationships**: Clear connections between entities
4. **Audit Trail**: Track all changes
5. **Multi-tenant Ready**: Tenant isolation built-in
6. **Flexible**: Support custom fields without schema changes

---

## Core Base Entities

### BaseEntity (Abstract)
All entities inherit from this base class.

```
- id: UUID (primary key)
- tenant_id: UUID (for multi-tenancy)
- created_at: DateTime
- created_by: UUID → User
- updated_at: DateTime
- updated_by: UUID → User
- is_active: Boolean (soft delete)
- is_deleted: Boolean
- deleted_at: DateTime
- deleted_by: UUID → User
```

### BaseTicket (Abstract)
Base class for Incident, Request, Change, Problem, etc.

Inherits: BaseEntity

```
- ticket_number: String (auto-generated, e.g., INC0001234, REQ0001234)
- title: String (max 255)
- description: Text
- status: String → TicketStatus
- priority: String → Priority (Critical, High, Medium, Low)
- urgency: String → Urgency
- impact: String → Impact
- category: UUID → Category
- subcategory: UUID → Subcategory
- assigned_to: UUID → User
- assigned_group: UUID → Group
- reported_by: UUID → User (requester)
- reported_date: DateTime
- resolved_at: DateTime
- resolved_by: UUID → User
- closed_at: DateTime
- closed_by: UUID → User
- resolution: Text
- close_notes: Text
- related_ci: UUID → ConfigurationItem (affected CI)
- related_service: UUID → Service
- sla_id: UUID → SLA
- sla_due_date: DateTime
- sla_breached: Boolean
- tags: JSON (flexible tagging)
- custom_fields: JSON (extensible custom data)
```

---

## Ticket Types (Module 1: Incident & Request Management)

### Incident
Inherits: BaseTicket

```
- incident_type: String (Hardware, Software, Network, Access, etc.)
- severity: String
- affected_users_count: Integer
- business_impact: Text
- workaround: Text
- root_cause: Text
- parent_problem_id: UUID → Problem (future)
```

### Request
Inherits: BaseTicket

```
- request_type: String (Service Request, Access Request, Information, etc.)
- catalog_item_id: UUID → CatalogItem
- approval_status: String (Pending, Approved, Rejected)
- approved_by: UUID → User
- approved_at: DateTime
- rejection_reason: Text
- fulfillment_notes: Text
```

### TicketStatus
Configuration table

```
- id: UUID
- name: String (New, Assigned, In Progress, Pending, Resolved, Closed, Cancelled)
- ticket_type: String (Incident, Request, Change, etc.)
- order: Integer (for workflow sequence)
- is_resolved_state: Boolean
- is_closed_state: Boolean
- color_code: String (UI visualization)
```

---

## User & Organization

### User
Inherits: BaseEntity

```
- user_id: String (login name)
- email: String (unique)
- first_name: String
- last_name: String
- full_name: String (computed)
- phone: String
- mobile: String
- job_title: String
- department_id: UUID → Department
- location_id: UUID → Location
- manager_id: UUID → User (self-reference)
- is_vip: Boolean
- language: String (default: en)
- timezone: String
- avatar_url: String
- auth_provider: String (local, sso, oauth)
- last_login: DateTime
- is_support_agent: Boolean
- is_admin: Boolean
- role_ids: Array<UUID> → Role (many-to-many)
```

### Group
Inherits: BaseEntity

```
- name: String
- description: Text
- group_type: String (Support Team, Approval Group, Department, etc.)
- email: String
- manager_id: UUID → User
- parent_group_id: UUID → Group (hierarchical)
- members: Array<UUID> → User (many-to-many through GroupMember)
- assignment_rules: JSON (automation rules)
```

### GroupMember
Junction table for User ↔ Group many-to-many

```
- id: UUID
- group_id: UUID → Group
- user_id: UUID → User
- role_in_group: String (Member, Leader, Approver)
- joined_at: DateTime
```

### Role
Inherits: BaseEntity

```
- name: String (Admin, Agent, End User, Manager)
- description: Text
- permissions: JSON (array of permission strings)
- is_system_role: Boolean (cannot be deleted)
```

---

## Organization Structure

### Department
Inherits: BaseEntity

```
- name: String
- code: String (unique)
- description: Text
- parent_department_id: UUID → Department (hierarchical)
- manager_id: UUID → User
- cost_center: String
```

### Location
Inherits: BaseEntity

```
- name: String
- address: Text
- city: String
- state: String
- country: String
- postal_code: String
- timezone: String
- phone: String
- location_type: String (Office, Data Center, Branch, Remote)
- parent_location_id: UUID → Location (hierarchical)
```

---

## Foundation Data (Extensible for CMDB)

### ConfigurationItem (CI)
Base for CMDB - can be extended for Asset Management

Inherits: BaseEntity

```
- ci_number: String (auto-generated, e.g., CI0001234)
- name: String
- ci_type: UUID → CIType
- ci_class: UUID → CIClass
- status: String (Active, Inactive, Retired, In Maintenance)
- owner: UUID → User
- support_group: UUID → Group
- location_id: UUID → Location
- manufacturer: String
- model: String
- serial_number: String
- asset_tag: String
- purchase_date: Date
- warranty_expiry: Date
- cost: Decimal
- depreciation: Decimal
- ip_address: String
- hostname: String
- description: Text
- notes: Text
- operational_status: String (Operational, Non-Operational, Under Repair)
- custom_attributes: JSON (flexible CI-specific data)
```

### CIType
Configuration for CI types

```
- id: UUID
- name: String (Server, Laptop, Switch, Router, Application, Database, etc.)
- icon: String
- color: String
- parent_type_id: UUID → CIType (hierarchical)
- attribute_schema: JSON (defines what attributes this type has)
```

### CIClass
Higher-level classification

```
- id: UUID
- name: String (Hardware, Software, Network, Service, Location, Person)
- description: Text
```

### CIRelationship
Relationships between CIs (CMDB relationships)

```
- id: UUID
- from_ci_id: UUID → ConfigurationItem
- to_ci_id: UUID → ConfigurationItem
- relationship_type: UUID → RelationshipType
- created_at: DateTime
- created_by: UUID → User
```

### RelationshipType
```
- id: UUID
- name: String (Runs On, Depends On, Connected To, Hosted By, Supports, etc.)
- reverse_name: String (e.g., "Hosts" is reverse of "Hosted By")
- description: Text
```

---

## Service Management (Foundation)

### Service
Business or IT services

Inherits: BaseEntity

```
- service_number: String (auto-generated)
- name: String
- description: Text
- service_type: String (Business Service, Technical Service)
- status: String (Active, Inactive, Planned, Retired)
- owner: UUID → User
- support_group: UUID → Group
- parent_service_id: UUID → Service (hierarchical)
- sla_id: UUID → SLA
- availability_target: Decimal (e.g., 99.9%)
- supporting_cis: Array<UUID> → ConfigurationItem (many-to-many)
```

### CatalogItem
Service catalog items for requests

Inherits: BaseEntity

```
- name: String
- short_description: String
- description: Text
- category_id: UUID → Category
- icon: String
- is_visible: Boolean (in portal)
- is_active: Boolean
- price: Decimal
- fulfillment_group: UUID → Group
- estimated_delivery: String (e.g., "2-3 business days")
- approval_required: Boolean
- approval_workflow_id: UUID → WorkflowDefinition
- form_schema: JSON (defines request form fields)
- order: Integer (display order)
```

---

## Categories & Classification

### Category
Hierarchical categorization for tickets and catalog items

Inherits: BaseEntity

```
- name: String
- description: Text
- category_type: String (Incident, Request, CI, Service)
- parent_category_id: UUID → Category (hierarchical)
- icon: String
- color: String
- is_active: Boolean
```

---

## SLA Management

### SLA
Service Level Agreement definitions

Inherits: BaseEntity

```
- name: String
- description: Text
- priority: String (links to ticket priority)
- response_time_minutes: Integer
- resolution_time_minutes: Integer
- is_active: Boolean
- applies_to: String (Incident, Request, All)
- business_hours_only: Boolean
- escalation_rules: JSON
```

### SLAHistory
Track SLA violations and metrics

```
- id: UUID
- ticket_id: UUID → BaseTicket (polymorphic)
- ticket_type: String (Incident, Request)
- sla_id: UUID → SLA
- due_date: DateTime
- completed_date: DateTime
- was_breached: Boolean
- breach_time_minutes: Integer
- pause_duration_minutes: Integer (time SLA was paused)
```

---

## Workflow & Automation

### WorkflowDefinition
Define reusable workflows (approvals, automation)

Inherits: BaseEntity

```
- name: String
- description: Text
- workflow_type: String (Approval, Escalation, Assignment, Notification)
- trigger_conditions: JSON (when to trigger)
- steps: JSON (workflow steps definition)
- is_active: Boolean
```

### WorkflowInstance
Track workflow execution

```
- id: UUID
- workflow_definition_id: UUID → WorkflowDefinition
- entity_id: UUID (ticket, request, etc.)
- entity_type: String
- status: String (Pending, In Progress, Completed, Cancelled)
- current_step: Integer
- started_at: DateTime
- completed_at: DateTime
- variables: JSON (workflow context data)
```

### ApprovalRequest
Track approvals

```
- id: UUID
- request_id: UUID → Request
- workflow_instance_id: UUID → WorkflowInstance
- approver_id: UUID → User
- approver_group_id: UUID → Group
- status: String (Pending, Approved, Rejected)
- approved_at: DateTime
- comments: Text
- sequence: Integer (for multi-level approvals)
```

---

## Communication & Collaboration

### Comment
Comments/notes on tickets

```
- id: UUID
- entity_id: UUID (ticket, CI, etc.)
- entity_type: String
- comment_type: String (Work Note, Customer Note, Resolution Note)
- content: Text
- created_by: UUID → User
- created_at: DateTime
- is_internal: Boolean (visible only to agents)
- is_edited: Boolean
- edited_at: DateTime
- mentions: Array<UUID> → User (tagged users)
- attachments: Array<UUID> → Attachment
```

### Attachment
File attachments

```
- id: UUID
- entity_id: UUID
- entity_type: String
- filename: String
- file_size: Integer (bytes)
- mime_type: String
- storage_path: String (S3, local, etc.)
- uploaded_by: UUID → User
- uploaded_at: DateTime
- is_public: Boolean
```

---

## Audit & History

### AuditLog
Track all changes to entities

```
- id: UUID
- entity_id: UUID
- entity_type: String
- action: String (CREATE, UPDATE, DELETE, STATUS_CHANGE)
- user_id: UUID → User
- timestamp: DateTime
- old_values: JSON
- new_values: JSON
- ip_address: String
- user_agent: String
```

### FieldHistory
Detailed field-level change tracking

```
- id: UUID
- entity_id: UUID
- entity_type: String
- field_name: String
- old_value: Text
- new_value: Text
- changed_by: UUID → User
- changed_at: DateTime
```

---

## Knowledge Base (Portal)

### KnowledgeArticle
Inherits: BaseEntity

```
- article_number: String (auto-generated)
- title: String
- content: Text (rich text/markdown)
- summary: Text
- category_id: UUID → Category
- author_id: UUID → User
- status: String (Draft, Published, Archived)
- published_at: DateTime
- view_count: Integer
- helpful_count: Integer
- not_helpful_count: Integer
- tags: Array<String>
- related_articles: Array<UUID> → KnowledgeArticle
- related_services: Array<UUID> → Service
- is_public: Boolean (visible in public portal)
- search_keywords: Text
```

---

## Notifications & Communication

### NotificationTemplate
Email/notification templates

Inherits: BaseEntity

```
- name: String
- description: Text
- event_type: String (Ticket Created, Status Changed, Assigned, etc.)
- subject: String (template)
- body: Text (template with variables)
- notification_type: String (Email, SMS, Push, In-App)
- is_active: Boolean
```

### Notification
Notification queue/history

```
- id: UUID
- user_id: UUID → User
- notification_type: String
- title: String
- message: Text
- entity_id: UUID
- entity_type: String
- is_read: Boolean
- read_at: DateTime
- sent_at: DateTime
- created_at: DateTime
```

---

## Multi-Tenancy

### Tenant
For SaaS multi-tenancy

```
- id: UUID
- name: String
- subdomain: String (unique, e.g., customer1.opsit.io)
- status: String (Active, Suspended, Trial, Cancelled)
- plan: String (Starter, Professional, Enterprise)
- max_users: Integer
- max_storage_gb: Integer
- created_at: DateTime
- subscription_ends_at: DateTime
- custom_domain: String (optional)
- branding: JSON (logo, colors, etc.)
- settings: JSON (tenant-specific config)
```

---

## Future Extensibility

### Asset (extends ConfigurationItem)
For full Asset Management module

```
Additional fields:
- lease_contract_id: UUID
- vendor_id: UUID → Vendor
- invoice_number: String
- po_number: String
- license_key: String
- license_expiry: Date
- assigned_to_user: UUID → User
- checkout_date: Date
- return_date: Date
```

### Employee (extends User)
For HR module

```
Additional fields:
- employee_number: String
- hire_date: Date
- termination_date: Date
- employment_type: String (Full-time, Part-time, Contractor)
- salary: Decimal (encrypted)
- reports_to: UUID → Employee
```

### Problem
For Problem Management module (future)

Inherits: BaseTicket

```
- problem_type: String
- root_cause_analysis: Text
- known_error: Boolean
- workaround: Text
- related_incidents: Array<UUID> → Incident
```

### Change
For Change Management module (future)

Inherits: BaseTicket

```
- change_type: String (Standard, Normal, Emergency)
- risk_level: String
- implementation_plan: Text
- backout_plan: Text
- scheduled_start: DateTime
- scheduled_end: DateTime
- cab_approval_required: Boolean
- affected_cis: Array<UUID> → ConfigurationItem
- related_incidents: Array<UUID> → Incident
```

---

## Database Indexes

Key indexes for performance:

```
- tenant_id on all tables (critical for multi-tenancy)
- ticket_number (unique)
- email (unique)
- status + assigned_to + assigned_group (ticket queues)
- created_at (sorting, time-based queries)
- Foreign key fields
- is_deleted + is_active (for filtering)
```

---

## Notes

1. **JSON Fields**: Use for flexibility without schema changes (custom_fields, tags, etc.)
2. **Soft Delete**: is_deleted flag instead of hard deletes (audit trail)
3. **Polymorphic Relations**: entity_id + entity_type pattern for flexible relationships
4. **Inheritance**: Use database table inheritance or JSON-based discriminators
5. **Extensibility**: Custom fields and attributes support future needs
6. **Multi-tenancy**: Every table has tenant_id for data isolation
