# OpsIT - Multi-Company Architecture (USP)

## Unique Selling Point

**OpsIT supports TWO deployment models:**

1. **Isolated Instances** (Traditional SaaS) - Each company gets their own dedicated instance
2. **Shared Instance** (Multi-Company) - Multiple companies share one instance with data separation

This flexibility is **unique in the ITSM market** and solves real business problems!

---

## Deployment Model Comparison

| Feature | Isolated Instances | Shared Instance (Multi-Company) |
|---------|-------------------|--------------------------------|
| **Data Isolation** | Complete (separate database) | Logical (same database, company_id filter) |
| **ITIL Processes** | Per company | Shared across companies |
| **Users** | Single company only | Can work with multiple companies |
| **Billing** | Per company | Consolidated billing |
| **Customization** | Full per company | Shared configuration |
| **Cost** | Higher (multiple instances) | Lower (shared infrastructure) |
| **Best For** | Enterprise, strict compliance | MSP, holding companies, partners |

---

## Use Case 1: MSP (Managed Service Provider) - Shared Instance

### Scenario
**"TechSupport MSP"** provides IT services to 10 small business customers.

### Architecture
```
OpsIT Instance: "TechSupport MSP"
├── Company: TechSupport MSP (Internal)
│   ├── Users: 15 support agents
│   ├── Groups: L1 Support, L2 Support, Network Team
│   └── Role: Can see ALL customer tickets
│
├── Company: Customer A Inc
│   ├── Users: 50 employees
│   ├── Tickets: 200 incidents, 50 requests
│   └── Can ONLY see their own data
│
├── Company: Customer B Corp
│   ├── Users: 30 employees
│   ├── Tickets: 150 incidents, 30 requests
│   └── Can ONLY see their own data
│
└── Company: Customer C Ltd
    ├── Users: 80 employees
    ├── Tickets: 300 incidents, 80 requests
    └── Can ONLY see their own data
```

### Benefits for MSP
- ✅ **One dashboard** to manage all customers
- ✅ **Cross-company reporting** (total tickets, SLA compliance across all customers)
- ✅ **Shared knowledge base** (but customer-specific articles too)
- ✅ **Unified support team** (agents see tickets from all customers)
- ✅ **Lower cost** (one instance, shared infrastructure)
- ✅ **Easier management** (one platform to maintain)

### Benefits for Customers
- ✅ **Data isolation** (cannot see other customers' data)
- ✅ **Professional portal** (branded with their company)
- ✅ **Access to expert support team**
- ✅ **Lower cost** (shared service model)

---

## Use Case 2: Enterprise Holding Company - Shared Instance

### Scenario
**"Global Corp Holdings"** owns 5 subsidiaries in different countries.

### Architecture
```
OpsIT Instance: "Global Corp"
├── Company: Global Corp Holdings (Parent)
│   ├── Users: 10 executives, IT directors
│   ├── Role: Can see ALL subsidiaries
│   └── Reporting: Consolidated view
│
├── Company: Global Corp USA (Subsidiary)
│   ├── Users: 200 employees
│   ├── Department: IT, HR, Finance, Sales
│   ├── Locations: New York, San Francisco
│   └── Can see: Own data + shared services
│
├── Company: Global Corp Germany GmbH (Subsidiary)
│   ├── Users: 150 employees
│   ├── Locations: Berlin, Munich
│   └── Can see: Own data + shared services
│
└── Company: Global Corp Singapore (Subsidiary)
    ├── Users: 100 employees
    ├── Locations: Singapore Office
    └── Can see: Own data + shared services
```

### Benefits
- ✅ **Corporate IT can see everything** (all subsidiaries)
- ✅ **Subsidiaries see only their data** (data privacy)
- ✅ **Shared IT services** (e.g., corporate email, ERP support)
- ✅ **Consolidated reporting** (board-level metrics)
- ✅ **Cost efficiency** (one platform license)
- ✅ **Easier audits** (one system to audit)

---

## Use Case 3: Partner Collaboration - Shared Instance

### Scenario
**"Acme Inc"** works closely with **"Partner Corp"** on joint projects.

### Architecture
```
OpsIT Instance: "Acme Partnership Platform"
├── Company: Acme Inc
│   ├── Users: 100 employees
│   └── Projects: Project X, Project Y
│
├── Company: Partner Corp
│   ├── Users: 50 employees
│   └── Projects: Project X (shared with Acme)
│
└── Shared Resources
    ├── Tickets: Joint project tickets (visible to both)
    ├── Knowledge Base: Shared documentation
    └── Service Catalog: Shared services
```

### Benefits
- ✅ **Cross-company collaboration** on shared tickets
- ✅ **Shared knowledge base** for joint projects
- ✅ **Clear visibility** (both companies see project status)
- ✅ **Single source of truth** for partnership work

---

## Use Case 4: Traditional Enterprise - Isolated Instance

### Scenario
**"MegaCorp"** wants full control and isolation.

### Architecture
```
OpsIT Instance: "MegaCorp Private"
└── Company: MegaCorp
    ├── Users: 5,000 employees
    ├── Departments: 50+ departments
    ├── Locations: 20+ offices worldwide
    └── Complete isolation (no other companies)
```

### Benefits
- ✅ **Complete data isolation** (most secure)
- ✅ **Full customization** (no shared constraints)
- ✅ **Compliance** (easier to audit, certify)
- ✅ **Performance** (dedicated resources)
- ✅ **Custom SLAs** (no shared infrastructure limits)

---

## Technical Implementation

### Database Schema Enhancement

All tables have `company_id` in addition to `tenant_id`:

```sql
-- tenant_id = SaaS instance (isolated or shared)
-- company_id = company within the instance

CREATE TABLE incidents (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,      -- which instance
    company_id UUID NOT NULL,      -- which company (data separation)
    ...
);

-- Row-level security
CREATE POLICY company_isolation ON incidents
    USING (
        company_id = current_setting('app.current_company_id')::UUID
        OR
        current_setting('app.user_can_see_all_companies')::BOOLEAN = TRUE
    );
```

### User Company Access

A user can have access to multiple companies (for MSP use case):

```sql
CREATE TABLE user_company_access (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    access_level VARCHAR(50) NOT NULL, -- read_only, full_access, admin
    can_create_tickets BOOLEAN DEFAULT TRUE,
    can_view_all_tickets BOOLEAN DEFAULT FALSE, -- for MSP agents
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_user_company UNIQUE (user_id, company_id)
);
```

### Multi-Company Query Example

```python
# Agent from MSP sees tickets from multiple companies
async def get_tickets_for_agent(agent_id: UUID, db: AsyncSession):
    # Get companies agent has access to
    company_access = await db.execute(
        select(UserCompanyAccess.company_id)
        .where(UserCompanyAccess.user_id == agent_id)
    )
    company_ids = [row.company_id for row in company_access.all()]

    # Get tickets from those companies
    tickets = await db.execute(
        select(Incident)
        .where(Incident.company_id.in_(company_ids))
        .where(Incident.is_deleted == False)
    )
    return tickets.scalars().all()

# End user sees only their company's tickets
async def get_tickets_for_user(user_id: UUID, company_id: UUID, db: AsyncSession):
    tickets = await db.execute(
        select(Incident)
        .where(Incident.company_id == company_id)
        .where(Incident.is_deleted == False)
    )
    return tickets.scalars().all()
```

---

## Configuration Options

### Instance Setup (Admin)

```json
{
  "instance_type": "shared", // or "isolated"
  "features": {
    "multi_company": true,
    "cross_company_tickets": false, // allow tickets visible to multiple companies
    "shared_knowledge_base": true,
    "consolidated_billing": true
  },
  "access_control": {
    "default_user_access": "single_company", // or "multi_company"
    "allow_cross_company_assignment": true, // MSP agents assigned to customer tickets
    "company_data_isolation": "strict" // strict, relaxed, shared
  }
}
```

### Company Settings

```json
{
  "company_id": "uuid",
  "visibility": {
    "allow_other_companies_to_see": false,
    "share_knowledge_base": true,
    "share_service_catalog": false
  },
  "branding": {
    "logo_url": "https://...",
    "primary_color": "#FF5733",
    "portal_subdomain": "acmeinc" // acmeinc.opsit.io
  }
}
```

---

## User Roles in Multi-Company

### 1. Platform Admin
- Can see ALL companies
- Manage platform configuration
- View consolidated reports
- Typical: MSP owner, Holding company CIO

### 2. Company Admin
- Can see ONLY their company
- Manage company settings
- Manage company users
- Typical: Customer IT manager

### 3. Support Agent (Multi-Company Access)
- Can see MULTIPLE companies (assigned)
- Create/manage tickets for those companies
- Typical: MSP support agent

### 4. End User
- Can see ONLY their company
- Create tickets, view own tickets
- Typical: Employee at customer company

---

## Portal Branding per Company

Each company can have branded portal:

```
https://customer-a.opsit.io  → Company A branding
https://customer-b.opsit.io  → Company B branding
https://msp.opsit.io         → MSP agent portal (sees all)
```

**Portal Customization:**
- Company logo
- Primary/secondary colors
- Custom domain (e.g., support.customer-a.com)
- Company-specific knowledge base
- Company-specific service catalog

---

## Billing Models

### Model 1: Per-Company Billing (MSP)
```
MSP pays OpsIT based on total usage:
- Customer A: 50 users × €10/user = €500/month
- Customer B: 30 users × €10/user = €300/month
- Customer C: 80 users × €10/user = €800/month
Total: €1,600/month

MSP charges customers:
- Customer A: €800/month (markup)
- Customer B: €500/month
- Customer C: €1,200/month
Total revenue: €2,500/month
MSP profit: €900/month
```

### Model 2: Enterprise Flat Rate
```
Global Corp pays OpsIT:
- Unlimited companies (subsidiaries)
- Up to 5,000 users
- €50,000/year flat rate
```

---

## Security & Compliance

### Data Isolation
- ✅ **Database-level**: All queries filtered by `company_id`
- ✅ **Row-level security**: PostgreSQL RLS policies
- ✅ **Application-level**: Middleware checks company access
- ✅ **Audit logging**: Log all cross-company access

### Compliance
- ✅ **GDPR**: Each company = separate data controller
- ✅ **ISO 27001**: Multi-company access controls documented
- ✅ **Data residency**: Company can choose data center region
- ✅ **Right to erasure**: Delete company data completely

### Security Best Practices
```python
# ALWAYS filter by company_id
@require_company_access
async def get_incident(incident_id: UUID, company_id: UUID, db: AsyncSession):
    incident = await db.execute(
        select(Incident)
        .where(
            Incident.id == incident_id,
            Incident.company_id == company_id  # CRITICAL: prevents data leakage
        )
    )
    return incident.scalar_one_or_none()
```

---

## Migration Path

### Start: Single Company (Simple)
```
Customer starts with:
- 1 company
- 100 users
- Isolated instance
```

### Grow: Add Subsidiaries
```
Customer expands:
- Parent company + 3 subsidiaries
- 500 users total
- Switch to shared instance (same tenant)
```

### Scale: MSP Model
```
MSP grows:
- 1 MSP company + 20 customer companies
- 1,000+ users
- Shared instance with multi-company access
```

---

## Competitive Advantage

### vs. ServiceNow
- ❌ ServiceNow: Complex multi-company setup, expensive
- ✅ OpsIT: Built-in, easy to configure, affordable

### vs. Jira Service Management
- ❌ Jira: Limited multi-company support
- ✅ OpsIT: Full multi-company with MSP mode

### vs. Freshservice
- ❌ Freshservice: Separate instances only
- ✅ OpsIT: Choose isolated OR shared

### vs. BMC Remedy
- ❌ BMC: Complex, legacy architecture
- ✅ OpsIT: Modern, cloud-native, flexible

---

## Marketing Message

**"One Platform, Endless Possibilities"**

> OpsIT is the only ITSM platform that lets YOU choose:
> - Run separate instances for complete isolation
> - OR share one instance across multiple companies
> - Perfect for MSPs, holding companies, and enterprises
> - Switch between models as you grow

**Target Customers:**
1. **MSPs** (Managed Service Providers) - Biggest opportunity!
2. **Holding Companies** - Parent + subsidiaries
3. **Large Enterprises** - Complex org structures
4. **VAR/Resellers** - Manage multiple customers
5. **Consultancies** - Support multiple clients

---

## Implementation Roadmap

### Phase 1 (MVP)
- ✅ Single company support (most customers start here)
- ✅ Database schema with `company_id`
- ✅ Basic company management

### Phase 2 (Month 4-6)
- ✅ Multi-company access for users
- ✅ MSP mode (agents see multiple companies)
- ✅ Company-specific branding
- ✅ Cross-company reporting

### Phase 3 (Month 7-12)
- ✅ Advanced company hierarchy (parent-child)
- ✅ Shared vs isolated CMDB per company
- ✅ Cross-company workflows
- ✅ Consolidated billing

---

## Summary

**OpsIT's Multi-Company Architecture is a GAME CHANGER:**

1. **Flexibility**: Choose isolated OR shared instances
2. **MSP-Ready**: Built for service providers from day one
3. **Cost-Effective**: Shared infrastructure, lower costs
4. **Secure**: Strict data isolation per company
5. **Scalable**: Start with 1 company, grow to 1,000+

**This is your USP - no competitor offers this flexibility!** 🚀

---

## Next Steps

1. Update database schema with multi-company tables
2. Implement `user_company_access` table
3. Create company switcher UI (for multi-company users)
4. Build MSP dashboard (see all customers)
5. Test data isolation thoroughly (security critical!)
6. Create marketing materials highlighting this USP

**This feature alone can win you the MSP market!** 🎯
