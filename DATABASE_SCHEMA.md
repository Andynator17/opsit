# OpsIT - PostgreSQL Database Schema

## Database Design

### PostgreSQL Version
- **Minimum**: PostgreSQL 14+
- **Recommended**: PostgreSQL 16+
- **Extensions**: uuid-ossp, pgcrypto, pg_trgm (full-text search), pgaudit (audit logging)

### Design Principles
1. **UUID Primary Keys** - All tables use UUIDs for primary keys
2. **Soft Deletes** - is_deleted flag instead of hard deletes
3. **Audit Trail** - created_at, updated_at, created_by, updated_by on all tables
4. **Multi-tenancy** - tenant_id on all tables
5. **JSONB** - For custom fields and flexible data
6. **Foreign Keys** - Enforce referential integrity
7. **Indexes** - Optimize common queries
8. **Partitioning** - For large tables (audit_logs, notifications)

---

## Core Tables

### tenants
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, suspended, trial, cancelled
    plan VARCHAR(50) NOT NULL DEFAULT 'starter', -- starter, professional, enterprise
    max_users INTEGER DEFAULT 10,
    max_storage_gb INTEGER DEFAULT 10,
    custom_domain VARCHAR(255),
    branding JSONB, -- {logo_url, primary_color, secondary_color}
    settings JSONB, -- tenant-specific configuration
    subscription_ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_tenants_subdomain ON tenants(subdomain) WHERE is_deleted = FALSE;
CREATE INDEX idx_tenants_status ON tenants(status) WHERE is_deleted = FALSE;
```

---

## Multi-Company Support (USP Feature)

### companies
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    company_code VARCHAR(50),

    -- Company Type
    company_type VARCHAR(50) NOT NULL DEFAULT 'internal', -- internal, customer, vendor, partner
    parent_company_id UUID REFERENCES companies(id),

    -- Contact Information
    primary_email VARCHAR(255),
    primary_phone VARCHAR(50),
    website VARCHAR(255),

    -- Address
    address_line1 VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),

    -- Business Details
    industry VARCHAR(100),
    employee_count INTEGER,

    -- Contract & SLA
    contract_start_date DATE,
    contract_end_date DATE,
    default_sla_id UUID, -- REFERENCES slas(id), added later
    support_tier VARCHAR(50), -- Basic, Standard, Premium, Enterprise

    -- Account Management
    account_manager_id UUID, -- REFERENCES users(id), added after users table

    -- Branding (for portal)
    logo_url VARCHAR(500),
    primary_color VARCHAR(20),
    secondary_color VARCHAR(20),
    portal_subdomain VARCHAR(100), -- e.g., customer-a.opsit.io

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active',

    -- Custom Fields
    custom_fields JSONB,

    -- Audit
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID, -- REFERENCES users(id)
    updated_by UUID, -- REFERENCES users(id)
    deleted_at TIMESTAMPTZ,
    deleted_by UUID, -- REFERENCES users(id)

    CONSTRAINT unique_company_code_per_tenant UNIQUE (tenant_id, company_code),
    CONSTRAINT unique_portal_subdomain UNIQUE (portal_subdomain)
);

CREATE INDEX idx_companies_tenant ON companies(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_companies_parent ON companies(parent_company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_companies_type ON companies(company_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_companies_status ON companies(status) WHERE is_deleted = FALSE;
```

---

## User Management

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Company Association (FOUNDATION DATA - KEY FOR MULTI-COMPANY)
    primary_company_id UUID NOT NULL REFERENCES companies(id), -- user's main company

    user_id VARCHAR(100) NOT NULL, -- login name
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255), -- Argon2id hash, NULL for SSO users
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    phone VARCHAR(50),
    mobile VARCHAR(50),
    job_title VARCHAR(100),

    -- Organization Structure
    department_id UUID REFERENCES departments(id),
    location_id UUID REFERENCES locations(id),
    manager_id UUID REFERENCES users(id),

    is_vip BOOLEAN NOT NULL DEFAULT FALSE,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    avatar_url VARCHAR(500),
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local', -- local, saml, oauth, ldap
    last_login TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,
    password_expires_at TIMESTAMPTZ,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret VARCHAR(255), -- encrypted TOTP secret
    is_support_agent BOOLEAN NOT NULL DEFAULT FALSE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_email_per_tenant UNIQUE (tenant_id, email),
    CONSTRAINT unique_user_id_per_tenant UNIQUE (tenant_id, user_id)
);

CREATE INDEX idx_users_tenant ON users(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_email ON users(email) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_company ON users(primary_company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_department ON users(department_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_manager ON users(manager_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_support_agent ON users(is_support_agent) WHERE is_deleted = FALSE AND is_support_agent = TRUE;
```

### user_company_access
**Multi-Company Support (USP)**: Users can have access to multiple companies
```sql
CREATE TABLE user_company_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    -- Access Level
    access_level VARCHAR(50) NOT NULL DEFAULT 'read_only', -- read_only, full_access, admin
    can_create_tickets BOOLEAN DEFAULT TRUE,
    can_view_all_tickets BOOLEAN DEFAULT FALSE, -- for MSP agents: see all company tickets
    can_manage_company BOOLEAN DEFAULT FALSE, -- company admin

    -- Use Case Examples:
    -- MSP Agent: can_view_all_tickets = TRUE (sees all customer tickets)
    -- Customer User: can_view_all_tickets = FALSE (sees only own tickets)
    -- Company Admin: can_manage_company = TRUE

    -- Audit
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ, -- optional expiry for temporary access
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id),

    CONSTRAINT unique_user_company UNIQUE (user_id, company_id)
);

CREATE INDEX idx_user_company_access_user ON user_company_access(user_id);
CREATE INDEX idx_user_company_access_company ON user_company_access(company_id);
CREATE INDEX idx_user_company_access_active ON user_company_access(user_id, company_id)
    WHERE revoked_at IS NULL AND (expires_at IS NULL OR expires_at > NOW());
```

### roles
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL, -- array of permission strings
    is_system_role BOOLEAN NOT NULL DEFAULT FALSE, -- cannot be deleted
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_role_name_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_roles_tenant ON roles(tenant_id) WHERE is_deleted = FALSE;
```

### user_roles
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),

    CONSTRAINT unique_user_role UNIQUE (user_id, role_id)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);
```

### groups
```sql
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(50) NOT NULL DEFAULT 'support_team', -- support_team, approval_group, department
    email VARCHAR(255),
    manager_id UUID REFERENCES users(id),
    parent_group_id UUID REFERENCES groups(id),
    assignment_rules JSONB, -- automation rules for ticket assignment
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_group_name_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_groups_tenant ON groups(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_groups_parent ON groups(parent_group_id) WHERE is_deleted = FALSE;
```

### group_members
```sql
CREATE TABLE group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID NOT NULL REFERENCES groups(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role_in_group VARCHAR(50) NOT NULL DEFAULT 'member', -- member, leader, approver
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_group_member UNIQUE (group_id, user_id)
);

CREATE INDEX idx_group_members_group ON group_members(group_id);
CREATE INDEX idx_group_members_user ON group_members(user_id);
```

---

## Organization Structure

### departments
```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    description TEXT,
    parent_department_id UUID REFERENCES departments(id),
    manager_id UUID REFERENCES users(id),
    cost_center VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_department_name_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_departments_tenant ON departments(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_departments_parent ON departments(parent_department_id) WHERE is_deleted = FALSE;
```

### locations
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    timezone VARCHAR(50),
    phone VARCHAR(50),
    location_type VARCHAR(50) NOT NULL DEFAULT 'office', -- office, data_center, branch, remote
    parent_location_id UUID REFERENCES locations(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_location_name_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_locations_tenant ON locations(tenant_id) WHERE is_deleted = FALSE;
```

---

## Ticket Management

### ticket_statuses
```sql
CREATE TABLE ticket_statuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL,
    ticket_type VARCHAR(50) NOT NULL, -- incident, request, problem, change
    order_num INTEGER NOT NULL, -- workflow sequence
    is_resolved_state BOOLEAN NOT NULL DEFAULT FALSE,
    is_closed_state BOOLEAN NOT NULL DEFAULT FALSE,
    color_code VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_status_per_type UNIQUE (tenant_id, ticket_type, name)
);

CREATE INDEX idx_ticket_statuses_tenant ON ticket_statuses(tenant_id);
CREATE INDEX idx_ticket_statuses_type ON ticket_statuses(ticket_type);
```

### categories
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_type VARCHAR(50) NOT NULL, -- incident, request, ci, service
    parent_category_id UUID REFERENCES categories(id),
    icon VARCHAR(100),
    color VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    CONSTRAINT unique_category_per_tenant UNIQUE (tenant_id, category_type, name, parent_category_id)
);

CREATE INDEX idx_categories_tenant ON categories(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_categories_type ON categories(category_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_categories_parent ON categories(parent_category_id) WHERE is_deleted = FALSE;
```

### incidents
```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    company_id UUID NOT NULL REFERENCES companies(id), -- MULTI-COMPANY: which company reported this
    ticket_number VARCHAR(50) NOT NULL, -- INC0001234
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    priority VARCHAR(50) NOT NULL DEFAULT 'medium', -- critical, high, medium, low
    urgency VARCHAR(50) NOT NULL DEFAULT 'medium',
    impact VARCHAR(50) NOT NULL DEFAULT 'medium',
    incident_type VARCHAR(100), -- hardware, software, network, access
    severity VARCHAR(50),
    category_id UUID REFERENCES categories(id),
    subcategory_id UUID REFERENCES categories(id),
    assigned_to_id UUID REFERENCES users(id),
    assigned_group_id UUID REFERENCES groups(id),
    reported_by_id UUID NOT NULL REFERENCES users(id),
    reported_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by_id UUID REFERENCES users(id),
    closed_at TIMESTAMPTZ,
    closed_by_id UUID REFERENCES users(id),
    resolution TEXT,
    close_notes TEXT,
    root_cause TEXT,
    workaround TEXT,
    business_impact TEXT,
    affected_users_count INTEGER,
    related_ci_id UUID, -- REFERENCES configuration_items(id), added later
    related_service_id UUID, -- REFERENCES services(id), added later
    parent_problem_id UUID, -- REFERENCES problems(id), future
    sla_id UUID, -- REFERENCES slas(id)
    sla_due_date TIMESTAMPTZ,
    sla_breached BOOLEAN NOT NULL DEFAULT FALSE,
    tags JSONB, -- flexible tagging
    custom_fields JSONB, -- extensible custom data
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_incident_number_per_tenant UNIQUE (tenant_id, ticket_number)
);

CREATE INDEX idx_incidents_tenant ON incidents(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_company ON incidents(company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_number ON incidents(ticket_number) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_status ON incidents(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_priority ON incidents(priority) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_assigned_to ON incidents(assigned_to_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_assigned_group ON incidents(assigned_group_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_reported_by ON incidents(reported_by_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_category ON incidents(category_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_created_at ON incidents(created_at) WHERE is_deleted = FALSE;
CREATE INDEX idx_incidents_sla_due ON incidents(sla_due_date) WHERE is_deleted = FALSE AND sla_due_date IS NOT NULL;

-- Full-text search index
CREATE INDEX idx_incidents_search ON incidents USING gin(to_tsvector('english', title || ' ' || description)) WHERE is_deleted = FALSE;
```

### requests
```sql
CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    company_id UUID NOT NULL REFERENCES companies(id), -- MULTI-COMPANY: which company submitted this request
    ticket_number VARCHAR(50) NOT NULL, -- REQ0001234
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    priority VARCHAR(50) NOT NULL DEFAULT 'medium',
    urgency VARCHAR(50) NOT NULL DEFAULT 'medium',
    impact VARCHAR(50) NOT NULL DEFAULT 'medium',
    request_type VARCHAR(100), -- service_request, access_request, information
    category_id UUID REFERENCES categories(id),
    subcategory_id UUID REFERENCES categories(id),
    catalog_item_id UUID, -- REFERENCES catalog_items(id)
    assigned_to_id UUID REFERENCES users(id),
    assigned_group_id UUID REFERENCES groups(id),
    reported_by_id UUID NOT NULL REFERENCES users(id),
    reported_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approval_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    approved_by_id UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by_id UUID REFERENCES users(id),
    closed_at TIMESTAMPTZ,
    closed_by_id UUID REFERENCES users(id),
    resolution TEXT,
    close_notes TEXT,
    fulfillment_notes TEXT,
    related_ci_id UUID,
    related_service_id UUID,
    sla_id UUID,
    sla_due_date TIMESTAMPTZ,
    sla_breached BOOLEAN NOT NULL DEFAULT FALSE,
    tags JSONB,
    custom_fields JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_request_number_per_tenant UNIQUE (tenant_id, ticket_number)
);

CREATE INDEX idx_requests_tenant ON requests(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_company ON requests(company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_number ON requests(ticket_number) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_status ON requests(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_assigned_to ON requests(assigned_to_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_reported_by ON requests(reported_by_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_approval_status ON requests(approval_status) WHERE is_deleted = FALSE;
CREATE INDEX idx_requests_created_at ON requests(created_at) WHERE is_deleted = FALSE;
```

### comments
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    entity_id UUID NOT NULL, -- incident_id, request_id, etc.
    entity_type VARCHAR(50) NOT NULL, -- incident, request, problem, change
    comment_type VARCHAR(50) NOT NULL DEFAULT 'work_note', -- work_note, customer_note, resolution_note
    content TEXT NOT NULL,
    is_internal BOOLEAN NOT NULL DEFAULT FALSE, -- visible only to agents
    is_edited BOOLEAN NOT NULL DEFAULT FALSE,
    edited_at TIMESTAMPTZ,
    mentions JSONB, -- array of user IDs who are mentioned
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_comments_tenant ON comments(tenant_id);
CREATE INDEX idx_comments_entity ON comments(entity_id, entity_type);
CREATE INDEX idx_comments_created_by ON comments(created_by);
CREATE INDEX idx_comments_created_at ON comments(created_at);
```

### attachments
```sql
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL, -- bytes
    mime_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL, -- S3 path or local path
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_attachments_tenant ON attachments(tenant_id);
CREATE INDEX idx_attachments_entity ON attachments(entity_id, entity_type);
CREATE INDEX idx_attachments_uploaded_by ON attachments(uploaded_by);
```

---

## Service Catalog

### catalog_items
```sql
CREATE TABLE catalog_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    description TEXT,
    category_id UUID REFERENCES categories(id),
    icon VARCHAR(100),
    is_visible BOOLEAN NOT NULL DEFAULT TRUE, -- visible in portal
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    price DECIMAL(10, 2) DEFAULT 0,
    fulfillment_group_id UUID REFERENCES groups(id),
    estimated_delivery VARCHAR(100), -- e.g., "2-3 business days"
    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
    approval_workflow_id UUID, -- REFERENCES workflow_definitions(id)
    form_schema JSONB, -- defines request form fields
    order_num INTEGER, -- display order
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_catalog_items_tenant ON catalog_items(tenant_id) WHERE is_deleted = FALSE AND is_active = TRUE;
CREATE INDEX idx_catalog_items_category ON catalog_items(category_id) WHERE is_deleted = FALSE;
```

---

## CMDB (Configuration Management Database)

### ci_classes
```sql
CREATE TABLE ci_classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL, -- Hardware, Software, Network, Service, Location, Person
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_ci_class_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_ci_classes_tenant ON ci_classes(tenant_id);
```

### ci_types
```sql
CREATE TABLE ci_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL, -- Server, Laptop, Switch, Router, Application, Database
    ci_class_id UUID NOT NULL REFERENCES ci_classes(id),
    icon VARCHAR(100),
    color VARCHAR(20),
    parent_type_id UUID REFERENCES ci_types(id),
    attribute_schema JSONB, -- defines what attributes this type has
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_ci_type_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_ci_types_tenant ON ci_types(tenant_id);
CREATE INDEX idx_ci_types_class ON ci_types(ci_class_id);
```

### configuration_items
```sql
CREATE TABLE configuration_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    ci_number VARCHAR(50) NOT NULL, -- CI0001234
    name VARCHAR(255) NOT NULL,
    ci_type_id UUID NOT NULL REFERENCES ci_types(id),
    ci_class_id UUID NOT NULL REFERENCES ci_classes(id),
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, inactive, retired, in_maintenance
    operational_status VARCHAR(50) NOT NULL DEFAULT 'operational', -- operational, non_operational, under_repair
    owner_id UUID REFERENCES users(id),
    support_group_id UUID REFERENCES groups(id),
    location_id UUID REFERENCES locations(id),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    asset_tag VARCHAR(100),
    purchase_date DATE,
    warranty_expiry DATE,
    cost DECIMAL(12, 2),
    depreciation DECIMAL(12, 2),
    ip_address VARCHAR(45), -- IPv6 support
    hostname VARCHAR(255),
    description TEXT,
    notes TEXT,
    custom_attributes JSONB, -- flexible CI-specific data
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_ci_number_per_tenant UNIQUE (tenant_id, ci_number)
);

CREATE INDEX idx_cis_tenant ON configuration_items(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_cis_number ON configuration_items(ci_number) WHERE is_deleted = FALSE;
CREATE INDEX idx_cis_type ON configuration_items(ci_type_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_cis_status ON configuration_items(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_cis_owner ON configuration_items(owner_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_cis_location ON configuration_items(location_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_cis_serial ON configuration_items(serial_number) WHERE is_deleted = FALSE;
```

### relationship_types
```sql
CREATE TABLE relationship_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL, -- Runs On, Depends On, Connected To, Hosted By, Supports
    reverse_name VARCHAR(100), -- e.g., "Hosts" is reverse of "Hosted By"
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_relationship_type_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_relationship_types_tenant ON relationship_types(tenant_id);
```

### ci_relationships
```sql
CREATE TABLE ci_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    from_ci_id UUID NOT NULL REFERENCES configuration_items(id),
    to_ci_id UUID NOT NULL REFERENCES configuration_items(id),
    relationship_type_id UUID NOT NULL REFERENCES relationship_types(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    CONSTRAINT no_self_relationship CHECK (from_ci_id != to_ci_id),
    CONSTRAINT unique_ci_relationship UNIQUE (from_ci_id, to_ci_id, relationship_type_id)
);

CREATE INDEX idx_ci_relationships_from ON ci_relationships(from_ci_id);
CREATE INDEX idx_ci_relationships_to ON ci_relationships(to_ci_id);
CREATE INDEX idx_ci_relationships_type ON ci_relationships(relationship_type_id);
```

---

## Service Management

### services
```sql
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    service_number VARCHAR(50) NOT NULL, -- SVC0001234
    name VARCHAR(255) NOT NULL,
    description TEXT,
    service_type VARCHAR(50) NOT NULL DEFAULT 'technical_service', -- business_service, technical_service
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, inactive, planned, retired
    owner_id UUID REFERENCES users(id),
    support_group_id UUID REFERENCES groups(id),
    parent_service_id UUID REFERENCES services(id),
    sla_id UUID, -- REFERENCES slas(id)
    availability_target DECIMAL(5, 2), -- e.g., 99.9%
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_service_number_per_tenant UNIQUE (tenant_id, service_number)
);

CREATE INDEX idx_services_tenant ON services(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_services_number ON services(service_number) WHERE is_deleted = FALSE;
CREATE INDEX idx_services_owner ON services(owner_id) WHERE is_deleted = FALSE;
```

### service_cis
```sql
CREATE TABLE service_cis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(id),
    ci_id UUID NOT NULL REFERENCES configuration_items(id),
    relationship_type VARCHAR(50) NOT NULL DEFAULT 'supports', -- supports, depends_on
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    CONSTRAINT unique_service_ci UNIQUE (service_id, ci_id)
);

CREATE INDEX idx_service_cis_service ON service_cis(service_id);
CREATE INDEX idx_service_cis_ci ON service_cis(ci_id);
```

---

## SLA Management

### slas
```sql
CREATE TABLE slas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low (links to ticket priority)
    response_time_minutes INTEGER NOT NULL, -- time to first response
    resolution_time_minutes INTEGER NOT NULL, -- time to resolution
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    applies_to VARCHAR(50) NOT NULL DEFAULT 'all', -- incident, request, all
    business_hours_only BOOLEAN NOT NULL DEFAULT TRUE,
    escalation_rules JSONB, -- escalation configuration
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_sla_per_tenant UNIQUE (tenant_id, name, priority)
);

CREATE INDEX idx_slas_tenant ON slas(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_slas_priority ON slas(priority) WHERE is_active = TRUE;
```

### sla_history
```sql
CREATE TABLE sla_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    ticket_id UUID NOT NULL, -- incident or request id
    ticket_type VARCHAR(50) NOT NULL, -- incident, request
    sla_id UUID NOT NULL REFERENCES slas(id),
    due_date TIMESTAMPTZ NOT NULL,
    completed_date TIMESTAMPTZ,
    was_breached BOOLEAN NOT NULL DEFAULT FALSE,
    breach_time_minutes INTEGER, -- how many minutes breached
    pause_duration_minutes INTEGER DEFAULT 0, -- time SLA was paused
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sla_history_tenant ON sla_history(tenant_id);
CREATE INDEX idx_sla_history_ticket ON sla_history(ticket_id, ticket_type);
CREATE INDEX idx_sla_history_sla ON sla_history(sla_id);
CREATE INDEX idx_sla_history_breached ON sla_history(was_breached) WHERE was_breached = TRUE;
```

---

## Knowledge Base

### knowledge_articles
```sql
CREATE TABLE knowledge_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    article_number VARCHAR(50) NOT NULL, -- KB0001234
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL, -- rich text/markdown
    summary TEXT,
    category_id UUID REFERENCES categories(id),
    author_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, published, archived
    published_at TIMESTAMPTZ,
    view_count INTEGER NOT NULL DEFAULT 0,
    helpful_count INTEGER NOT NULL DEFAULT 0,
    not_helpful_count INTEGER NOT NULL DEFAULT 0,
    tags JSONB, -- array of tags
    is_public BOOLEAN NOT NULL DEFAULT FALSE, -- visible in public portal
    search_keywords TEXT, -- additional keywords for search
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_article_number_per_tenant UNIQUE (tenant_id, article_number)
);

CREATE INDEX idx_knowledge_tenant ON knowledge_articles(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_knowledge_number ON knowledge_articles(article_number) WHERE is_deleted = FALSE;
CREATE INDEX idx_knowledge_status ON knowledge_articles(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_knowledge_author ON knowledge_articles(author_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_knowledge_category ON knowledge_articles(category_id) WHERE is_deleted = FALSE;

-- Full-text search
CREATE INDEX idx_knowledge_search ON knowledge_articles USING gin(to_tsvector('english', title || ' ' || content || ' ' || COALESCE(search_keywords, ''))) WHERE is_deleted = FALSE;
```

### article_related
```sql
CREATE TABLE article_related (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES knowledge_articles(id),
    related_article_id UUID NOT NULL REFERENCES knowledge_articles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT no_self_related CHECK (article_id != related_article_id),
    CONSTRAINT unique_article_related UNIQUE (article_id, related_article_id)
);

CREATE INDEX idx_article_related_article ON article_related(article_id);
```

---

## Workflows & Automation

### workflow_definitions
```sql
CREATE TABLE workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL, -- approval, escalation, assignment, notification
    trigger_conditions JSONB NOT NULL, -- when to trigger
    steps JSONB NOT NULL, -- workflow steps definition
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_workflows_tenant ON workflow_definitions(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_workflows_type ON workflow_definitions(workflow_type) WHERE is_active = TRUE;
```

### workflow_instances
```sql
CREATE TABLE workflow_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    workflow_definition_id UUID NOT NULL REFERENCES workflow_definitions(id),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, in_progress, completed, cancelled
    current_step INTEGER NOT NULL DEFAULT 1,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    variables JSONB, -- workflow context data
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workflow_instances_tenant ON workflow_instances(tenant_id);
CREATE INDEX idx_workflow_instances_workflow ON workflow_instances(workflow_definition_id);
CREATE INDEX idx_workflow_instances_entity ON workflow_instances(entity_id, entity_type);
CREATE INDEX idx_workflow_instances_status ON workflow_instances(status);
```

### approval_requests
```sql
CREATE TABLE approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    request_id UUID NOT NULL REFERENCES requests(id),
    workflow_instance_id UUID REFERENCES workflow_instances(id),
    approver_id UUID REFERENCES users(id),
    approver_group_id UUID REFERENCES groups(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected
    approved_at TIMESTAMPTZ,
    comments TEXT,
    sequence INTEGER NOT NULL DEFAULT 1, -- for multi-level approvals
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT approval_must_have_approver CHECK (approver_id IS NOT NULL OR approver_group_id IS NOT NULL)
);

CREATE INDEX idx_approval_requests_tenant ON approval_requests(tenant_id);
CREATE INDEX idx_approval_requests_request ON approval_requests(request_id);
CREATE INDEX idx_approval_requests_approver ON approval_requests(approver_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(status);
```

---

## Notifications

### notification_templates
```sql
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(100) NOT NULL, -- ticket_created, status_changed, assigned, etc.
    subject VARCHAR(500), -- template
    body TEXT NOT NULL, -- template with variables
    notification_type VARCHAR(50) NOT NULL DEFAULT 'email', -- email, sms, push, in_app
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    CONSTRAINT unique_template_per_tenant UNIQUE (tenant_id, event_type, notification_type)
);

CREATE INDEX idx_notification_templates_tenant ON notification_templates(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_notification_templates_event ON notification_templates(event_type) WHERE is_active = TRUE;
```

### notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID NOT NULL REFERENCES users(id),
    notification_type VARCHAR(50) NOT NULL, -- email, sms, push, in_app
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    entity_id UUID,
    entity_type VARCHAR(50),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Partitioning by month for performance
CREATE TABLE notifications_2024_01 PARTITION OF notifications
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Continue with monthly partitions...

CREATE INDEX idx_notifications_tenant ON notifications(tenant_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_entity ON notifications(entity_id, entity_type);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
```

---

## Audit & History

### audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, STATUS_CHANGE
    user_id UUID REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT
) PARTITION BY RANGE (timestamp);

-- Partitioning by month
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Continue with monthly partitions...

CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_id, entity_type);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### field_history
```sql
CREATE TABLE field_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (changed_at);

-- Partitioning by month
CREATE TABLE field_history_2024_01 PARTITION OF field_history
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE INDEX idx_field_history_entity ON field_history(entity_id, entity_type);
CREATE INDEX idx_field_history_field ON field_history(field_name);
CREATE INDEX idx_field_history_changed_at ON field_history(changed_at);
```

---

## System Configuration

### system_settings
```sql
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    setting_key VARCHAR(255) NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_setting_per_tenant UNIQUE (tenant_id, setting_key)
);

CREATE INDEX idx_system_settings_tenant ON system_settings(tenant_id);
```

### webhooks
```sql
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    events JSONB NOT NULL, -- array of event types
    secret VARCHAR(255), -- for signature verification
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_webhooks_tenant ON webhooks(tenant_id) WHERE is_active = TRUE;
```

---

## Database Functions & Triggers

### Update timestamp trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to all other tables...
```

### Auto-generate ticket numbers
```sql
CREATE SEQUENCE incident_number_seq;

CREATE OR REPLACE FUNCTION generate_incident_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL THEN
        NEW.ticket_number := 'INC' || LPAD(nextval('incident_number_seq')::TEXT, 7, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_incident_number BEFORE INSERT ON incidents
    FOR EACH ROW EXECUTE FUNCTION generate_incident_number();

-- Similar for requests, problems, changes, CIs, etc.
```

### Row-Level Security (RLS) for Multi-tenancy
```sql
-- Enable RLS on all tables
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

-- Create policy to enforce tenant isolation
CREATE POLICY tenant_isolation_policy ON incidents
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Apply to all tables...
```

---

## Materialized Views (for Performance)

### Ticket statistics
```sql
CREATE MATERIALIZED VIEW mv_ticket_stats AS
SELECT
    tenant_id,
    'incident' as ticket_type,
    status,
    priority,
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, NOW()) - created_at)) / 3600) as avg_resolution_hours
FROM incidents
WHERE is_deleted = FALSE
GROUP BY tenant_id, status, priority, DATE_TRUNC('day', created_at);

CREATE UNIQUE INDEX ON mv_ticket_stats (tenant_id, ticket_type, status, priority, date);

-- Refresh periodically (hourly via cron job)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ticket_stats;
```

---

## Backup & Maintenance

```sql
-- Automated daily backups
-- pg_dump -Fc -U opsit -d opsit_production > backup_$(date +%Y%m%d).dump

-- Point-in-time recovery (PITR)
-- Configure WAL archiving in postgresql.conf

-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex
REINDEX DATABASE opsit_production;
```

---

## Database Migration Strategy

Using Alembic (Python):

```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Create tenants table
    op.create_table('tenants', ...)
    # Create users table
    op.create_table('users', ...)
    # etc.

def downgrade():
    # Rollback changes
    op.drop_table('users')
    op.drop_table('tenants')
```

---

## Connection Pool Settings

```python
# SQLAlchemy connection pool
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/opsit"
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # connections per worker
    max_overflow=10,
    pool_pre_ping=True,  # verify connections
    pool_recycle=3600,  # recycle connections after 1 hour
)
```

---

## Database Performance Tuning

```sql
-- PostgreSQL configuration (postgresql.conf)

shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
```

---

## Estimated Table Sizes (1000 users, 1 year)

```
tenants:             ~100 rows          ~100 KB
users:              ~1,000 rows        ~1 MB
incidents:         ~50,000 rows        ~50 MB
requests:          ~30,000 rows        ~30 MB
comments:         ~200,000 rows       ~200 MB
attachments:       ~100,000 rows       ~100 MB (metadata only, files stored separately)
configuration_items: ~10,000 rows      ~10 MB
audit_logs:      ~1,000,000 rows     ~1 GB (with partitioning)
notifications:     ~500,000 rows      ~500 MB (with partitioning)

Total database size (without attachments): ~2-3 GB/year
```
