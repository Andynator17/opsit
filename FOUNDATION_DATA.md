# OpsIT - Foundation Data (Master Data Management)

## Overview
Foundation data is the organizational and reference data that forms the backbone of the ITSM platform. This data must be well-structured, hierarchical, and maintainable.

---

## Core Foundation Data Entities

### 1. Company / Organization (Multi-level)

#### companies
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    company_code VARCHAR(50) UNIQUE,

    -- Company Type
    company_type VARCHAR(50) NOT NULL DEFAULT 'internal', -- internal, customer, vendor, partner
    parent_company_id UUID REFERENCES companies(id), -- for holding structures

    -- Contact Information
    primary_email VARCHAR(255),
    primary_phone VARCHAR(50),
    website VARCHAR(255),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),

    -- Business Details
    industry VARCHAR(100), -- IT, Finance, Healthcare, Manufacturing, etc.
    employee_count INTEGER,
    annual_revenue DECIMAL(15, 2),
    tax_id VARCHAR(50), -- VAT, EIN, etc.

    -- Contract & SLA
    contract_start_date DATE,
    contract_end_date DATE,
    default_sla_id UUID REFERENCES slas(id),
    support_tier VARCHAR(50), -- Basic, Standard, Premium, Enterprise

    -- Billing
    billing_address_same_as_primary BOOLEAN DEFAULT TRUE,
    billing_address_line1 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_country VARCHAR(100),
    billing_contact_id UUID REFERENCES contacts(id),

    -- Account Management
    account_manager_id UUID REFERENCES users(id), -- internal account manager
    primary_contact_id UUID REFERENCES contacts(id), -- customer's main contact

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, inactive, suspended

    -- Custom Fields
    custom_fields JSONB,

    -- Audit
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_company_code_per_tenant UNIQUE (tenant_id, company_code)
);

CREATE INDEX idx_companies_tenant ON companies(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_companies_parent ON companies(parent_company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_companies_type ON companies(company_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_companies_status ON companies(status) WHERE is_deleted = FALSE;
```

**Use Cases:**
- **Internal Company**: Your own organization structure
- **Customer Company**: B2B customers using your ITSM service
- **Vendor Company**: Third-party vendors you work with
- **Partner Company**: Business partners, resellers

**Hierarchy Example:**
```
Acme Corporation (Holding)
├── Acme Germany GmbH
│   ├── Acme Germany IT Services
│   └── Acme Germany Consulting
├── Acme France SARL
└── Acme UK Ltd
```

---

### 2. Contacts (CRM - Customer/User Contacts)

#### contacts
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    title VARCHAR(50), -- Mr., Mrs., Dr., Prof.
    job_title VARCHAR(100),

    -- Company Relationship
    company_id UUID NOT NULL REFERENCES companies(id),
    department_id UUID REFERENCES departments(id),
    reports_to_contact_id UUID REFERENCES contacts(id), -- organizational hierarchy

    -- Contact Information
    primary_email VARCHAR(255) NOT NULL,
    secondary_email VARCHAR(255),
    work_phone VARCHAR(50),
    mobile_phone VARCHAR(50),
    home_phone VARCHAR(50),
    preferred_contact_method VARCHAR(50) DEFAULT 'email', -- email, phone, mobile

    -- Address (if different from company)
    address_line1 VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),

    -- Location
    office_location_id UUID REFERENCES locations(id),

    -- Contact Role
    contact_type VARCHAR(50) NOT NULL DEFAULT 'user', -- user, admin, billing, technical, executive
    is_primary_contact BOOLEAN DEFAULT FALSE, -- primary contact for company
    is_billing_contact BOOLEAN DEFAULT FALSE,
    is_technical_contact BOOLEAN DEFAULT FALSE,
    is_vip BOOLEAN DEFAULT FALSE,

    -- Communication Preferences
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    receive_notifications BOOLEAN DEFAULT TRUE,
    receive_marketing BOOLEAN DEFAULT FALSE,

    -- Portal Access (if contact also has user account)
    user_id UUID REFERENCES users(id), -- link to user account if they have portal access

    -- Notes
    notes TEXT,

    -- Social/External IDs
    linkedin_url VARCHAR(255),
    external_id VARCHAR(100), -- ID from external CRM

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, inactive, left_company

    -- Audit
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_email_per_company UNIQUE (tenant_id, company_id, primary_email)
);

CREATE INDEX idx_contacts_tenant ON contacts(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_contacts_company ON contacts(company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_contacts_email ON contacts(primary_email) WHERE is_deleted = FALSE;
CREATE INDEX idx_contacts_user ON contacts(user_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_contacts_department ON contacts(department_id) WHERE is_deleted = FALSE;
```

**Contact vs User:**
- **Contact**: External person (customer, vendor contact) - CRM data
- **User**: Internal staff or portal user with login credentials

A contact can become a user if they need portal access.

---

### 3. Departments (Organizational Units)

#### departments (Enhanced)
```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50), -- HR, IT, FIN, OPS, etc.
    description TEXT,

    -- Company Association
    company_id UUID NOT NULL REFERENCES companies(id), -- which company does this dept belong to

    -- Hierarchy
    parent_department_id UUID REFERENCES departments(id),
    level INTEGER, -- 1 = top level, 2 = sub-department, etc.
    hierarchy_path VARCHAR(500), -- e.g., "1.2.3" for querying entire hierarchy

    -- Management
    manager_id UUID REFERENCES users(id),
    director_id UUID REFERENCES users(id), -- higher level manager

    -- Business Details
    cost_center VARCHAR(100),
    budget_code VARCHAR(100),
    department_type VARCHAR(50), -- IT, Finance, HR, Operations, Sales, Support, etc.

    -- Support Configuration
    support_group_id UUID REFERENCES groups(id), -- linked support team
    default_sla_id UUID REFERENCES slas(id),

    -- Contact
    email VARCHAR(255), -- department email (e.g., hr@company.com)
    phone VARCHAR(50),

    -- Location
    primary_location_id UUID REFERENCES locations(id),

    -- Statistics (updated periodically)
    employee_count INTEGER DEFAULT 0,
    open_ticket_count INTEGER DEFAULT 0,

    -- Custom Fields
    custom_fields JSONB,

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_dept_name_per_company UNIQUE (tenant_id, company_id, name),
    CONSTRAINT unique_dept_code_per_company UNIQUE (tenant_id, company_id, code)
);

CREATE INDEX idx_departments_tenant ON departments(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_departments_company ON departments(company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_departments_parent ON departments(parent_department_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_departments_manager ON departments(manager_id) WHERE is_deleted = FALSE;
```

**Department Hierarchy Example:**
```
IT Department (level 1)
├── IT Operations (level 2)
│   ├── Network Operations (level 3)
│   ├── Server Operations (level 3)
│   └── Database Administration (level 3)
├── IT Support (level 2)
│   ├── Service Desk (level 3)
│   └── Field Support (level 3)
└── IT Development (level 2)
    ├── Application Development (level 3)
    └── DevOps (level 3)
```

---

### 4. Locations (Physical Sites)

#### locations (Enhanced)
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50), -- HQ, NYC-01, LON-DC1, etc.
    description TEXT,

    -- Company Association
    company_id UUID NOT NULL REFERENCES companies(id),

    -- Hierarchy
    parent_location_id UUID REFERENCES locations(id), -- e.g., Building -> Floor -> Room
    level INTEGER,

    -- Location Type
    location_type VARCHAR(50) NOT NULL DEFAULT 'office',
    -- office, data_center, warehouse, branch, retail_store, manufacturing_plant,
    -- remote, home_office, co_working_space, customer_site

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(3), -- ISO 3166-1 alpha-3

    -- Geographic Coordinates (for mapping)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Contact
    phone VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(255),

    -- Business Hours
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    business_hours JSONB, -- {"monday": {"open": "09:00", "close": "17:00"}, ...}

    -- Capacity & Details
    floor_number VARCHAR(20),
    building_number VARCHAR(50),
    room_number VARCHAR(50),
    square_meters DECIMAL(10, 2),
    capacity_people INTEGER, -- how many people can work here

    -- Facilities
    has_parking BOOLEAN DEFAULT FALSE,
    has_cafeteria BOOLEAN DEFAULT FALSE,
    has_datacenter BOOLEAN DEFAULT FALSE,
    accessibility_features TEXT,

    -- IT Infrastructure
    network_segment VARCHAR(100), -- IP range, VLAN info
    internet_provider VARCHAR(100),
    backup_power BOOLEAN DEFAULT FALSE, -- UPS, generator

    -- Management
    site_manager_id UUID REFERENCES users(id),
    facilities_manager_id UUID REFERENCES users(id),

    -- Support
    support_group_id UUID REFERENCES groups(id), -- local IT support team

    -- Statistics
    employee_count INTEGER DEFAULT 0,
    device_count INTEGER DEFAULT 0,

    -- Emergency
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(50),
    evacuation_plan_url VARCHAR(500),

    -- Custom Fields
    custom_fields JSONB,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, inactive, under_construction, closed
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT unique_location_code_per_company UNIQUE (tenant_id, company_id, code)
);

CREATE INDEX idx_locations_tenant ON locations(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_locations_company ON locations(company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_locations_parent ON locations(parent_location_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_locations_type ON locations(location_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_locations_country ON locations(country) WHERE is_deleted = FALSE;
CREATE INDEX idx_locations_city ON locations(city) WHERE is_deleted = FALSE;
```

**Location Hierarchy Example:**
```
New York Headquarters (Building)
├── Floor 1
│   ├── Lobby
│   ├── Reception
│   └── Conference Room A
├── Floor 2
│   ├── IT Operations Center
│   ├── Server Room 2A
│   └── Network Room 2B
└── Floor 3
    ├── Executive Offices
    └── Board Room
```

---

### 5. Users (Enhanced with Company/Department links)

#### users (Enhanced)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Authentication
    user_id VARCHAR(100) NOT NULL, -- login name
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),

    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    middle_name VARCHAR(100),
    preferred_name VARCHAR(100),

    -- Company & Department (FOUNDATION LINKS)
    company_id UUID NOT NULL REFERENCES companies(id), -- which company does this user belong to
    department_id UUID REFERENCES departments(id),
    location_id UUID REFERENCES locations(id),

    -- Job Information
    job_title VARCHAR(100),
    employee_id VARCHAR(50), -- HR employee number
    employment_type VARCHAR(50) DEFAULT 'full_time', -- full_time, part_time, contractor, intern
    hire_date DATE,
    termination_date DATE,

    -- Organizational Hierarchy
    manager_id UUID REFERENCES users(id),
    reports_to_user_id UUID REFERENCES users(id), -- direct manager

    -- Contact Information
    phone VARCHAR(50),
    mobile VARCHAR(50),
    extension VARCHAR(20),

    -- Business Details
    cost_center VARCHAR(100),
    business_unit VARCHAR(100),
    division VARCHAR(100),

    -- User Type & Access
    user_type VARCHAR(50) NOT NULL DEFAULT 'internal', -- internal, external, contractor, vendor
    is_vip BOOLEAN NOT NULL DEFAULT FALSE,
    vip_reason TEXT, -- why is this user VIP?

    -- Support Agent Details
    is_support_agent BOOLEAN NOT NULL DEFAULT FALSE,
    agent_level VARCHAR(50), -- L1, L2, L3, Manager
    support_specialization TEXT, -- Network, Database, Applications, etc.

    -- Portal Access
    has_portal_access BOOLEAN DEFAULT FALSE,
    portal_role VARCHAR(50), -- end_user, requester, approver

    -- Communication Preferences
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    time_format VARCHAR(20) DEFAULT '24h',

    -- Avatar
    avatar_url VARCHAR(500),

    -- Authentication
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
    external_auth_id VARCHAR(255), -- ID from SSO/LDAP
    last_login TIMESTAMPTZ,
    last_password_change TIMESTAMPTZ,
    password_expires_at TIMESTAMPTZ,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,

    -- MFA
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    mfa_backup_codes JSONB,

    -- Permissions
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    roles JSONB, -- array of role names

    -- Linked Contact
    contact_id UUID REFERENCES contacts(id), -- if this user is also a contact

    -- Custom Fields
    custom_fields JSONB,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, inactive, on_leave, terminated
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT unique_email_per_tenant UNIQUE (tenant_id, email),
    CONSTRAINT unique_user_id_per_tenant UNIQUE (tenant_id, user_id),
    CONSTRAINT unique_employee_id_per_company UNIQUE (tenant_id, company_id, employee_id)
);

CREATE INDEX idx_users_tenant ON users(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_company ON users(company_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_department ON users(department_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_location ON users(location_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_manager ON users(manager_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_email ON users(email) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_support_agent ON users(is_support_agent) WHERE is_support_agent = TRUE;
```

---

## Foundation Data Relationships

### Visual Hierarchy
```
Tenant (SaaS Customer)
├── Companies (multiple)
│   ├── Departments (hierarchical)
│   │   └── Users
│   ├── Locations (hierarchical)
│   │   └── Users
│   └── Contacts (CRM)
│       └── Can become Users (if portal access needed)
│
└── Master Data
    ├── Categories
    ├── SLAs
    ├── Groups
    └── Roles
```

### Key Relationships
1. **Tenant → Companies**: One tenant can have multiple companies (holding structure)
2. **Company → Departments**: Each company has multiple departments
3. **Company → Locations**: Each company has multiple locations
4. **Company → Contacts**: Each company has multiple contacts (CRM)
5. **Company → Users**: Each company has multiple users (employees)
6. **User → Department**: Each user belongs to one department
7. **User → Location**: Each user works at one primary location
8. **Contact → User**: A contact can have a user account (for portal access)
9. **Department → Users**: Each department has multiple users
10. **Location → Users**: Each location has multiple users

---

## Foundation Data Use Cases

### 1. Multi-Company Support
```
Scenario: MSP (Managed Service Provider) serving multiple customers

Tenant: "TechSupport MSP"
├── Company: "Customer A Inc" (customer)
│   ├── Departments: IT, Finance, HR
│   ├── Locations: NYC Office, LA Office
│   └── Users: 50 employees
├── Company: "Customer B Corp" (customer)
│   ├── Departments: Operations, Sales
│   ├── Locations: Chicago HQ
│   └── Users: 30 employees
└── Company: "TechSupport MSP" (internal)
    ├── Departments: Service Desk, Network Ops
    ├── Locations: NOC, Office
    └── Users: 20 support agents
```

### 2. Enterprise with Multiple Subsidiaries
```
Tenant: "Global Corp"
└── Company: "Global Corp Holdings" (parent)
    ├── Company: "Global Corp USA" (subsidiary)
    │   ├── Departments: IT, Sales, Support
    │   └── Locations: New York, San Francisco
    ├── Company: "Global Corp Europe GmbH" (subsidiary)
    │   ├── Departments: IT, Sales
    │   └── Locations: Berlin, Munich
    └── Company: "Global Corp Asia Ltd" (subsidiary)
        ├── Departments: IT, Operations
        └── Locations: Singapore, Tokyo
```

### 3. Single Company (Simple)
```
Tenant: "Acme Inc"
└── Company: "Acme Inc"
    ├── Departments: IT, HR, Finance, Operations
    ├── Locations: HQ, Branch Office, Data Center
    └── Users: 200 employees
```

---

## API Endpoints for Foundation Data

### Companies
```
GET    /api/v1/companies                     # List all companies
POST   /api/v1/companies                     # Create company
GET    /api/v1/companies/{id}                # Get company details
PATCH  /api/v1/companies/{id}                # Update company
DELETE /api/v1/companies/{id}                # Delete company
GET    /api/v1/companies/{id}/departments    # Get company departments
GET    /api/v1/companies/{id}/locations      # Get company locations
GET    /api/v1/companies/{id}/users          # Get company users
GET    /api/v1/companies/{id}/contacts       # Get company contacts
GET    /api/v1/companies/{id}/tickets        # Get company tickets
```

### Contacts (CRM)
```
GET    /api/v1/contacts                      # List all contacts
POST   /api/v1/contacts                      # Create contact
GET    /api/v1/contacts/{id}                 # Get contact details
PATCH  /api/v1/contacts/{id}                 # Update contact
DELETE /api/v1/contacts/{id}                 # Delete contact
POST   /api/v1/contacts/{id}/create-user     # Convert contact to user (portal access)
GET    /api/v1/contacts/{id}/tickets         # Get contact's tickets
```

### Departments
```
GET    /api/v1/departments                   # List all departments
POST   /api/v1/departments                   # Create department
GET    /api/v1/departments/{id}              # Get department details
PATCH  /api/v1/departments/{id}              # Update department
DELETE /api/v1/departments/{id}              # Delete department
GET    /api/v1/departments/{id}/users        # Get department users
GET    /api/v1/departments/{id}/hierarchy    # Get full department tree
GET    /api/v1/departments/{id}/tickets      # Get department tickets
```

### Locations
```
GET    /api/v1/locations                     # List all locations
POST   /api/v1/locations                     # Create location
GET    /api/v1/locations/{id}                # Get location details
PATCH  /api/v1/locations/{id}                # Update location
DELETE /api/v1/locations/{id}                # Delete location
GET    /api/v1/locations/{id}/users          # Get location users
GET    /api/v1/locations/{id}/assets         # Get location assets/CIs
GET    /api/v1/locations/{id}/hierarchy      # Get location tree
GET    /api/v1/locations/{id}/tickets        # Get location tickets
```

### Users (Enhanced)
```
GET    /api/v1/users                         # List all users
POST   /api/v1/users                         # Create user
GET    /api/v1/users/{id}                    # Get user details
PATCH  /api/v1/users/{id}                    # Update user
DELETE /api/v1/users/{id}                    # Deactivate user
GET    /api/v1/users/{id}/organization       # Get user's company, dept, location
GET    /api/v1/users/{id}/hierarchy          # Get user's org chart (manager, reports)
GET    /api/v1/users/{id}/tickets            # Get user's tickets
```

---

## Data Import/Export

### Import Foundation Data
For initial setup or migration, support CSV/Excel import:

```
POST /api/v1/import/companies
POST /api/v1/import/departments
POST /api/v1/import/locations
POST /api/v1/import/users
POST /api/v1/import/contacts
```

**Import Format (CSV):**
```csv
# users.csv
email,first_name,last_name,company_code,department_code,location_code,job_title,manager_email
john.doe@example.com,John,Doe,ACME,IT,NYC-HQ,IT Manager,jane.smith@example.com
```

### Export Foundation Data
```
GET /api/v1/export/companies?format=csv
GET /api/v1/export/users?format=excel
GET /api/v1/export/departments?format=json
```

---

## Foundation Data Validation Rules

### Company
- ✅ Company name must be unique per tenant
- ✅ Parent company cannot create circular reference
- ✅ Must have at least one active location
- ✅ Tax ID format validation per country

### Department
- ✅ Department code must be unique per company
- ✅ Cannot delete department with active users
- ✅ Manager must be a user in same company
- ✅ Parent department must be in same company

### Location
- ✅ Location code must be unique per company
- ✅ Country code must be valid ISO 3166-1
- ✅ Timezone must be valid IANA timezone
- ✅ Cannot delete location with active users or assets

### User
- ✅ Email must be unique per tenant
- ✅ Employee ID must be unique per company
- ✅ Manager must be in same company
- ✅ Department must belong to user's company
- ✅ Location must belong to user's company
- ✅ Termination date must be after hire date

### Contact
- ✅ Email must be unique per company
- ✅ Primary contact: only one per company
- ✅ Cannot delete contact if linked to user account
- ✅ Cannot delete contact if linked to active tickets

---

## Foundation Data Dashboard (Admin)

### Company Overview
- Total companies
- Active companies
- Companies by type (internal, customer, vendor, partner)
- Companies by industry
- Companies by support tier
- Companies with expiring contracts (next 30 days)

### User Overview
- Total users
- Active users
- Users by company
- Users by department
- Users by location
- Users by employment type
- VIP users
- Support agents by level

### Department Overview
- Total departments
- Departments by company
- Department hierarchy tree view
- Departments by employee count
- Departments with most tickets

### Location Overview
- Total locations
- Locations by type
- Locations by country
- Locations with most users
- Locations with most assets
- Map view (using lat/long)

---

## ITIL Foundation Data Integration

### Service Catalog
Link catalog items to:
- ✅ **Company**: Different catalog items for different customers
- ✅ **Department**: Department-specific requests (e.g., HR onboarding)
- ✅ **Location**: Location-specific requests (e.g., parking pass)

### Incidents
Link incidents to:
- ✅ **Company**: Which customer reported this
- ✅ **Department**: Affected department
- ✅ **Location**: Incident location
- ✅ **User**: Reported by user (from company)

### CMDB
Link configuration items to:
- ✅ **Company**: Asset owner
- ✅ **Department**: Asset assigned to department
- ✅ **Location**: Physical location of asset
- ✅ **User**: Asset assigned to user

---

## MVP Priority for Foundation Data

### Phase 1 (MVP - Week 1-2)
1. ✅ **Companies** (basic - single company for most customers)
2. ✅ **Departments** (flat structure, no hierarchy)
3. ✅ **Locations** (flat structure)
4. ✅ **Users** (with company, department, location links)

### Phase 2 (Months 4-6)
5. ✅ **Contacts** (CRM functionality)
6. ✅ **Company Hierarchy** (parent-child relationships)
7. ✅ **Department Hierarchy** (org chart)
8. ✅ **Location Hierarchy** (building → floor → room)

### Phase 3 (Months 7-12)
9. ✅ **Advanced CRM** (contact notes, activities, opportunities)
10. ✅ **Organization Chart Visualization**
11. ✅ **Location Map View**
12. ✅ **Bulk Import/Export Tools**

---

## Summary

Foundation data (Company, Department, Location, Users, Contacts) is the **backbone** of OpsIT:

1. **Everything links to foundation data**: Tickets, Assets, Services, SLAs
2. **Hierarchical structures**: Support complex organizations
3. **Multi-company support**: B2B SaaS, MSPs, holding companies
4. **CRM integration**: Contacts can become users
5. **ITIL compliant**: Aligns with ITIL service asset and configuration management

**Key takeaway**: Spend time designing foundation data correctly - it's very hard to change later! ✅
