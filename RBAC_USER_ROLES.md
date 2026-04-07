# OpsIT - Role-Based Access Control (RBAC)

## Overview
OpsIT implements a flexible RBAC system with **5 core user roles**, each with distinct permissions and user experience. Roles are designed to align with ITIL best practices and support multi-company architecture.

---

## Role Hierarchy

```
┌─────────────────────────────────────────┐
│          Platform Admin                 │  Level 5: Full platform control
├─────────────────────────────────────────┤
│      Developer (Workflow Builder)       │  Level 4: Custom development
├─────────────────────────────────────────┤
│    IT Operations (L2/L3 Support)        │  Level 3: Advanced support
├─────────────────────────────────────────┤
│    Helpdesk (Service Desk Agent)        │  Level 2: Ticket management
├─────────────────────────────────────────┤
│       End User (Portal User)            │  Level 1: Self-service
└─────────────────────────────────────────┘
```

---

## Role Definitions

### 1. End User (Portal Access Only)

**Target Audience**: Employees, customers who need IT support

**Access**: Frontend Portal ONLY (no backend access)

**Portal URL**: `https://{company}.opsit.io/portal`

**Capabilities:**
- ✅ Create incidents (report issues)
- ✅ Submit requests from service catalog
- ✅ View own tickets (incidents and requests)
- ✅ Add comments to own tickets
- ✅ Upload attachments
- ✅ Browse knowledge base (self-help articles)
- ✅ View notifications (maintenance, outages, problems)
- ✅ View ticket status and SLA countdown
- ✅ Rate knowledge articles (helpful/not helpful)
- ✅ Update own profile

**Cannot:**
- ❌ See other users' tickets
- ❌ Assign or reassign tickets
- ❌ Change ticket priority
- ❌ Access backend/admin interface
- ❌ See internal work notes
- ❌ Access CMDB or configuration items
- ❌ Create or edit knowledge articles

**UI Features:**
- Dashboard: My open tickets, quick actions
- Ticket submission forms (incident, request)
- Knowledge base search
- Notifications center
- Profile settings

**ITIL Mapping**: Service Desk Customer, End User

**Database Fields:**
```sql
users table:
- is_support_agent: FALSE
- is_admin: FALSE
- has_portal_access: TRUE
- portal_role: 'end_user'
```

---

### 2. Helpdesk / Service Desk Agent (L1 Support)

**Target Audience**: Service desk agents, L1 support team

**Access**: Backend System (Agent Interface)

**Portal URL**: `https://app.opsit.io/agent`

**Capabilities:**
- ✅ View ALL open tickets (all or filtered by company)
- ✅ Create tickets on behalf of users
- ✅ Assign tickets to self or other agents
- ✅ Reassign tickets to other agents or groups
- ✅ Update ticket details (description, category, priority)
- ✅ Add work notes (internal and customer-facing)
- ✅ Change ticket status (New → In Progress → Pending → Resolved)
- ✅ Link tickets to knowledge base articles
- ✅ View knowledge base (read-only)
- ✅ View incident/request queues
- ✅ View SLA status and breaches
- ✅ Search tickets (advanced filters)
- ✅ View CMDB (read-only)
- ✅ View user profiles and company information

**Cannot:**
- ❌ Close tickets (only resolve, requires user confirmation)
- ❌ Delete tickets
- ❌ Create or edit knowledge articles
- ❌ Modify CMDB (configuration items)
- ❌ Access admin settings
- ❌ Modify workflows or SLAs
- ❌ Create users or groups

**Multi-Company Considerations:**
- **Single Company Agent**: Sees only tickets from assigned company
- **MSP Agent**: Can see tickets from MULTIPLE customer companies (via `user_company_access` table)

**UI Features:**
- Agent dashboard (ticket queues, team performance)
- Ticket list (all, my tickets, team queue, unassigned)
- Ticket detail view (full ticket lifecycle)
- Quick actions (assign, update status, add note)
- Knowledge base (search and link)
- User lookup
- Basic reporting (my stats, team stats)

**ITIL Mapping**: Service Desk Agent, Incident Coordinator, Request Fulfiller

**Database Fields:**
```sql
users table:
- is_support_agent: TRUE
- is_admin: FALSE
- agent_level: 'L1'
- support_specialization: NULL or 'General Support'

user_company_access (for MSP):
- can_view_all_tickets: TRUE (see all company tickets)
- can_create_tickets: TRUE
```

---

### 3. IT Operations / L2/L3 Support

**Target Audience**: Specialized support teams (Network, Database, Application, Infrastructure)

**Access**: Backend System with Advanced Features

**Portal URL**: `https://app.opsit.io/ops`

**Capabilities:**
- ✅ All Helpdesk capabilities PLUS:
- ✅ Assigned to specific assignment groups (e.g., Network Ops, Database Team)
- ✅ Receive escalated tickets from L1
- ✅ Receive tasks from request fulfillment
- ✅ Resolve AND close tickets
- ✅ Perform root cause analysis
- ✅ Create problem records (link multiple incidents)
- ✅ View and edit CMDB (configuration items)
- ✅ Create relationships between CIs
- ✅ Perform impact analysis (CI dependencies)
- ✅ Create and edit knowledge articles (from resolved incidents)
- ✅ View advanced reports (trend analysis, recurring issues)
- ✅ Manage SLA exceptions
- ✅ Escalate to L3 or vendors

**Cannot:**
- ❌ Delete tickets or CIs
- ❌ Access admin settings (users, groups, workflows)
- ❌ Modify SLA definitions
- ❌ Access tenant/company configuration

**Assignment Groups:**
- Network Operations
- Server Operations
- Database Administration
- Application Support
- Security Team
- Desktop Support
- Infrastructure Team

**UI Features:**
- Ops dashboard (team queue, SLA at-risk, escalations)
- Advanced ticket management
- CMDB editor
- Problem management
- Knowledge article creator
- Impact analysis tool
- Advanced reporting

**ITIL Mapping**: Technical Support, Specialist Support, Problem Analyst, Configuration Manager

**Database Fields:**
```sql
users table:
- is_support_agent: TRUE
- is_admin: FALSE
- agent_level: 'L2' or 'L3'
- support_specialization: 'Network', 'Database', 'Applications', etc.

groups:
- group_type: 'support_team'
- name: 'Network Operations', 'Database Team', etc.

group_members:
- user_id: ops_user_id
- role_in_group: 'member', 'leader'
```

---

### 4. Admin (Platform Administrator)

**Target Audience**: IT managers, platform administrators

**Access**: Full Backend Access + Admin Panel

**Portal URL**: `https://app.opsit.io/admin`

**Capabilities:**
- ✅ All IT Ops capabilities PLUS:
- ✅ User management (create, edit, deactivate users)
- ✅ Group management (create teams, assign members)
- ✅ Company management (create, edit companies) - **Multi-company**
- ✅ Department and location management
- ✅ Role and permission management
- ✅ SLA configuration (create, edit SLAs)
- ✅ Service catalog management (create catalog items, forms)
- ✅ Category management (incident, request categories)
- ✅ Workflow configuration (approval workflows, escalation rules)
- ✅ Notification template management
- ✅ Knowledge base administration (publish, archive articles)
- ✅ System settings (branding, portal customization)
- ✅ Audit log access (view all system changes)
- ✅ Advanced reports and analytics
- ✅ Data import/export
- ✅ Integration management (SSO, webhooks, API keys)

**Cannot:**
- ❌ Edit workflows (reserved for Developer role)
- ❌ Access database directly
- ❌ Modify platform code

**Multi-Company Considerations:**
- **Company Admin**: Can manage only their company (users, groups, settings)
- **Platform Admin (MSP)**: Can manage ALL companies and see consolidated data

**UI Features:**
- Admin dashboard (platform health, usage stats)
- User management (CRUD, roles, permissions)
- Company management (multi-company setup)
- SLA and workflow configuration
- Service catalog builder
- System settings (branding, integrations)
- Audit logs and compliance reports
- Tenant management (billing, subscription)

**ITIL Mapping**: Service Desk Manager, Incident Manager, Problem Manager, Change Manager, Service Owner, Configuration Manager

**Database Fields:**
```sql
users table:
- is_support_agent: TRUE
- is_admin: TRUE
- agent_level: 'Manager' or 'Admin'

user_company_access (for MSP Platform Admin):
- can_manage_company: TRUE (for all companies)
- can_view_all_tickets: TRUE
```

---

### 5. Developer (Workflow Builder) - EXTRA

**Target Audience**: Technical architects, process engineers, developers

**Access**: Backend + Developer Tools

**Portal URL**: `https://app.opsit.io/dev`

**Capabilities:**
- ✅ All Admin capabilities PLUS:
- ✅ Workflow builder (visual workflow editor)
- ✅ Custom script editor (Python, JavaScript)
- ✅ Automation rules (triggers, conditions, actions)
- ✅ Custom field builder (dynamic forms)
- ✅ API integration builder
- ✅ Custom report builder (SQL queries, charts)
- ✅ Webhook configuration
- ✅ Business rules editor
- ✅ Custom app builder (low-code/no-code)
- ✅ Template editor (email, notifications)
- ✅ Advanced integrations (REST API, GraphQL)

**Cannot:**
- ❌ Access production database directly (read-only via query builder)
- ❌ Deploy to production without approval (requires admin approval)

**Use Cases:**
- Build custom approval workflows
- Create automated ticket routing rules
- Design custom dashboards
- Build integrations with external systems (Slack, Teams, Jira)
- Automate recurring tasks (e.g., auto-close resolved tickets after 7 days)

**UI Features:**
- Workflow visual builder (drag-and-drop)
- Script editor (syntax highlighting, testing)
- Automation rules designer
- Custom field builder
- Integration wizard
- API documentation and testing
- Version control (workflow versions)

**ITIL Mapping**: Process Architect, Automation Engineer, Integration Specialist

**Database Fields:**
```sql
users table:
- is_support_agent: TRUE
- is_admin: TRUE
- is_developer: TRUE
- agent_level: 'Developer'

permissions:
- workflow.create
- workflow.edit
- workflow.delete
- script.execute
- api.create
```

---

## Permissions Matrix

### Core Permissions

| Permission | End User | Helpdesk (L1) | IT Ops (L2/L3) | Admin | Developer |
|------------|----------|---------------|----------------|-------|-----------|
| **Tickets** |
| Create incident | ✅ Own | ✅ All | ✅ All | ✅ All | ✅ All |
| View incident | ✅ Own | ✅ All | ✅ All | ✅ All | ✅ All |
| Edit incident | ✅ Own | ✅ All | ✅ All | ✅ All | ✅ All |
| Assign incident | ❌ | ✅ | ✅ | ✅ | ✅ |
| Resolve incident | ❌ | ✅ | ✅ | ✅ | ✅ |
| Close incident | ❌ | ❌ | ✅ | ✅ | ✅ |
| Delete incident | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Requests** |
| Submit request | ✅ | ✅ | ✅ | ✅ | ✅ |
| View request | ✅ Own | ✅ All | ✅ All | ✅ All | ✅ All |
| Approve request | ❌ | ❌ | ✅ Assigned | ✅ | ✅ |
| Fulfill request | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Knowledge Base** |
| View articles | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create articles | ❌ | ❌ | ✅ | ✅ | ✅ |
| Edit articles | ❌ | ❌ | ✅ | ✅ | ✅ |
| Publish articles | ❌ | ❌ | ❌ | ✅ | ✅ |
| Delete articles | ❌ | ❌ | ❌ | ✅ | ✅ |
| **CMDB** |
| View CIs | ❌ | ✅ Read-only | ✅ | ✅ | ✅ |
| Create CIs | ❌ | ❌ | ✅ | ✅ | ✅ |
| Edit CIs | ❌ | ❌ | ✅ | ✅ | ✅ |
| Delete CIs | ❌ | ❌ | ❌ | ✅ | ✅ |
| Manage relationships | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Users & Groups** |
| View users | ❌ | ✅ Basic | ✅ Basic | ✅ Full | ✅ Full |
| Create users | ❌ | ❌ | ❌ | ✅ | ✅ |
| Edit users | ❌ | ❌ | ❌ | ✅ | ✅ |
| Deactivate users | ❌ | ❌ | ❌ | ✅ | ✅ |
| Manage groups | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Configuration** |
| View SLAs | ❌ | ✅ | ✅ | ✅ | ✅ |
| Edit SLAs | ❌ | ❌ | ❌ | ✅ | ✅ |
| Manage workflows | ❌ | ❌ | ❌ | ❌ | ✅ |
| System settings | ❌ | ❌ | ❌ | ✅ | ✅ |
| Custom scripts | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Reporting** |
| View basic reports | ✅ Own | ✅ Team | ✅ Team | ✅ All | ✅ All |
| View advanced reports | ❌ | ❌ | ✅ | ✅ | ✅ |
| Create custom reports | ❌ | ❌ | ❌ | ✅ | ✅ |
| Export data | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Audit** |
| View audit logs | ❌ | ❌ | ❌ | ✅ | ✅ |
| View compliance reports | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## Multi-Company Role Considerations

### Scenario 1: Single Company (Traditional)
```
Company: Acme Inc
├── End Users: 100 employees (see only Acme tickets)
├── Helpdesk: 5 agents (see only Acme tickets)
├── IT Ops: 10 specialists (see only Acme tickets)
└── Admin: 2 IT managers (manage Acme)
```

### Scenario 2: MSP with Multiple Customers
```
MSP Platform
├── MSP Internal Company
│   ├── Helpdesk: 15 agents (see ALL customer tickets)
│   ├── IT Ops: 10 specialists (assigned to customer companies)
│   └── Admin: 3 managers (manage ALL companies)
│
├── Customer A Company
│   ├── End Users: 50 employees (see only Customer A tickets)
│   └── Company Admin: 1 IT manager (manage Customer A only)
│
└── Customer B Company
    ├── End Users: 30 employees (see only Customer B tickets)
    └── Company Admin: 1 IT manager (manage Customer B only)
```

**Key Difference:**
- **MSP Agents**: `user_company_access.can_view_all_tickets = TRUE` for multiple companies
- **Customer Users**: Only see their own company data

---

## Role Assignment & Management

### Database Implementation

```sql
-- User with primary company
INSERT INTO users (
    id, tenant_id, primary_company_id, email,
    is_support_agent, is_admin, agent_level
) VALUES (
    uuid_generate_v4(),
    'tenant-uuid',
    'company-uuid',
    'agent@msp.com',
    TRUE,  -- is support agent
    FALSE, -- not admin
    'L1'   -- helpdesk level
);

-- Grant access to multiple companies (for MSP agents)
INSERT INTO user_company_access (
    user_id, company_id, access_level,
    can_view_all_tickets, can_create_tickets
) VALUES
    ('agent-uuid', 'customer-a-uuid', 'full_access', TRUE, TRUE),
    ('agent-uuid', 'customer-b-uuid', 'full_access', TRUE, TRUE),
    ('agent-uuid', 'customer-c-uuid', 'full_access', TRUE, TRUE);
```

### API Permission Check Example

```python
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def check_permission(
    user: User,
    required_permission: str,
    company_id: UUID | None = None,
    db: AsyncSession = Depends(get_db)
):
    # Check if user has the permission
    if not has_permission(user, required_permission):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Check company access (for multi-company)
    if company_id:
        has_access = await check_company_access(user.id, company_id, db)
        if not has_access:
            raise HTTPException(status_code=403, detail="No access to this company")

    return True

# Usage in endpoint
@router.get("/incidents")
async def list_incidents(
    company_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(check_permission(required_permission="incident.view"))
):
    # User has permission, proceed
    incidents = await get_incidents_for_company(company_id, db)
    return incidents
```

---

## UI/UX Differences per Role

### 1. End User Portal
**Theme**: Simple, friendly, self-service focused

**Navigation:**
- Home / Dashboard
- Create Incident
- Service Catalog (Browse Requests)
- My Tickets
- Knowledge Base
- Notifications
- Profile

**Dashboard Widgets:**
- Quick Actions (Create Incident, Browse Catalog)
- My Open Tickets (list)
- Recent Notifications
- Knowledge Base Search

---

### 2. Helpdesk Agent Interface
**Theme**: Efficient, ticket-centric, fast actions

**Navigation:**
- Dashboard
- All Tickets (incidents + requests)
- My Assigned Tickets
- Team Queue
- Unassigned Queue
- Knowledge Base
- User Lookup
- Reports (basic)

**Dashboard Widgets:**
- My Open Tickets (count + list)
- Team Queue (count + list)
- SLA At-Risk Tickets
- Unassigned Tickets
- Today's Stats (created, resolved, closed)
- Team Performance

**Key Features:**
- Quick assign (drag-and-drop)
- Bulk actions
- Fast status updates
- In-line commenting
- Knowledge article suggestions

---

### 3. IT Ops Interface
**Theme**: Technical, detail-oriented, CMDB-focused

**Navigation:**
- Dashboard
- Tickets (advanced filters)
- Problem Management
- CMDB (Configuration Items)
- Knowledge Base (create/edit)
- Impact Analysis
- Reports (advanced)

**Dashboard Widgets:**
- My Assignment Group Queue
- Escalated Tickets
- SLA Breaches (team)
- Root Cause Analysis Queue
- CI Changes (recent)
- Recurring Incidents

**Key Features:**
- CMDB editor
- Impact analysis tool
- Problem record creation
- Knowledge article authoring
- Advanced search

---

### 4. Admin Interface
**Theme**: Management, configuration, oversight

**Navigation:**
- Dashboard (platform overview)
- Tickets (all visibility)
- Users & Groups
- Companies (multi-company)
- Configuration
  - SLAs
  - Categories
  - Service Catalog
  - Workflows
  - Notifications
- CMDB
- Knowledge Base (admin)
- Reports & Analytics
- Audit Logs
- System Settings

**Dashboard Widgets:**
- Platform Health
- Active Users
- Ticket Volume (by company)
- SLA Compliance (global)
- User Activity
- Storage Usage
- Upcoming Contract Renewals (for customers)

---

### 5. Developer Interface
**Theme**: Technical, builder, automation

**Navigation:**
- Dashboard
- Workflow Builder
- Automation Rules
- Custom Fields
- Scripts & Functions
- Integrations
- API Management
- Reports (custom SQL)
- Version Control

**Dashboard Widgets:**
- Active Workflows
- Automation Rule Triggers (today)
- API Usage Stats
- Script Execution Logs
- Integration Health

**Key Features:**
- Visual workflow builder (drag-and-drop)
- Code editor (Monaco editor)
- API testing console
- Webhook debugger
- Custom report builder (SQL + charts)

---

## Role Transition / Promotion Path

```
End User → Helpdesk (L1) → IT Ops (L2/L3) → Admin → Developer
   ↑            ↑               ↑             ↑         ↑
   │            │               │             │         │
Portal      Backend         Advanced      Management  Builder
Access      Access          Support       Access      Access
```

**Typical Career Path:**
1. **Start**: End User (employee needing support)
2. **Join Support**: Helpdesk Agent (L1)
3. **Specialize**: IT Ops (L2/L3 in Network, Database, etc.)
4. **Manage**: Admin (team lead, manager)
5. **Build**: Developer (process engineer, architect)

---

## Permission Examples in Code

### Python/FastAPI Permissions

```python
# Decorator for permission checks
def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not has_permission(user, permission):
                raise HTTPException(status_code=403, detail="Permission denied")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/incidents")
@require_permission("incident.create")
async def create_incident(
    incident: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # User has permission, create incident
    return await incident_service.create(incident, current_user, db)
```

### React/Frontend Permissions

```typescript
// Permission context
const PermissionContext = React.createContext<string[]>([]);

export const usePermission = (permission: string): boolean => {
  const permissions = useContext(PermissionContext);
  return permissions.includes(permission);
};

// Usage in component
const TicketList: React.FC = () => {
  const canCreateIncident = usePermission('incident.create');
  const canAssignTicket = usePermission('incident.assign');

  return (
    <div>
      {canCreateIncident && (
        <Button onClick={createIncident}>Create Incident</Button>
      )}
      {canAssignTicket && (
        <Select options={agents} onChange={assignTicket} />
      )}
    </div>
  );
};
```

---

## Summary

**OpsIT's 5-Role System:**

1. **End User** - Self-service portal, create tickets, view knowledge base
2. **Helpdesk (L1)** - Manage all tickets, assign, update, resolve
3. **IT Ops (L2/L3)** - Specialized support, CMDB, problem management, close tickets
4. **Admin** - Platform management, user/company/config administration
5. **Developer** - Workflow builder, automation, custom apps

**Key Features:**
- ✅ Clear role separation
- ✅ ITIL aligned
- ✅ Multi-company support (MSP agents see multiple companies)
- ✅ Flexible permissions
- ✅ Role-based UI (different experience per role)
- ✅ Easy to understand and implement

**Next Steps:**
1. Implement permission system in backend
2. Create role-based UI views in frontend
3. Build admin panel for role management
4. Test multi-company access control
5. Document permission assignment process
