# OpsIT - ITIL Processes Implementation

## Overview
OpsIT implements ITIL v4 (Information Technology Infrastructure Library) best practices and processes to ensure industry-standard service management.

---

## ITIL Service Value System in OpsIT

### Guiding Principles
1. **Focus on value** - Every feature delivers value to end users and IT teams
2. **Start where you are** - Simple implementation, extensible architecture
3. **Progress iteratively** - MVP first, then expand
4. **Collaborate and promote visibility** - Transparent workflows, clear communication
5. **Think and work holistically** - Integrated modules, not silos
6. **Keep it simple and practical** - Modern UX, avoid unnecessary complexity
7. **Optimize and automate** - Built-in automation, smart workflows

---

## ITIL Practices Implemented in OpsIT

### Phase 1: MVP (Incident & Request Management)

#### 1. Incident Management
**ITIL Definition**: Minimize the negative impact of incidents by restoring normal service operation as quickly as possible.

**OpsIT Implementation**:

```
Workflow:
1. Incident Logging → 2. Categorization → 3. Prioritization →
4. Initial Diagnosis → 5. Escalation (if needed) → 6. Investigation & Resolution →
7. Resolution & Recovery → 8. Incident Closure

Key Features:
- Incident identification and logging (portal, email, API)
- Incident categorization and prioritization (Priority/Urgency matrix)
- Major incident management (VIP flag, high priority handling)
- Incident matching (similar incidents, known errors)
- SLA tracking and breach notifications
- Assignment rules (auto-assign based on category/CI)
- Escalation workflows (time-based, manager escalation)
- Link to affected CIs and services
- Resolution tracking
- Metrics: MTTR, First Contact Resolution, Backlog, SLA compliance
```

**Database Mapping**:
- Entity: `Incident` (extends `BaseTicket`)
- Related: `ConfigurationItem`, `Service`, `User`, `Group`, `SLA`, `KnowledgeArticle`

**ITIL Roles**:
- Service Desk Agent → `User` with `is_support_agent: true`
- Incident Manager → `User` in management `Group`
- End User → `User` with `role: "End User"`

---

#### 2. Service Request Management (Request Fulfillment)
**ITIL Definition**: Support the agreed quality of a service by handling all predefined, user-initiated service requests in an effective and user-friendly manner.

**OpsIT Implementation**:

```
Workflow:
1. Request Submission (via Service Catalog) → 2. Request Validation →
3. Approval (if required) → 4. Fulfillment → 5. Closure

Key Features:
- Service catalog (pre-defined request types)
- Request form templates (per catalog item)
- Multi-level approval workflows (automatic routing)
- Fulfillment tracking and updates
- Estimated delivery times
- SLA tracking for requests
- Integration with HR (access requests, onboarding)
- Request templates for common scenarios
- Metrics: Fulfillment time, Approval time, Request backlog
```

**Database Mapping**:
- Entity: `Request` (extends `BaseTicket`)
- Related: `CatalogItem`, `ApprovalRequest`, `WorkflowInstance`, `User`, `Group`

**ITIL Roles**:
- Request Fulfiller → `User` in fulfillment `Group`
- Approver → `User` in approval `Group`
- Service Catalog Manager → Admin managing `CatalogItem`

---

#### 3. Knowledge Management
**ITIL Definition**: Maintain and improve the effective, efficient, and convenient use of knowledge across the organization.

**OpsIT Implementation**:

```
Key Features:
- Knowledge base (searchable articles)
- Article lifecycle (Draft → Review → Published → Archived)
- Rich text editor with images/attachments
- Categories and tags
- Related articles and services
- Article ratings (helpful/not helpful)
- View count tracking
- Integration with incidents/requests (suggest articles)
- Public vs internal articles
- Search with relevance ranking
- Metrics: Article usage, Search success rate, User ratings
```

**Database Mapping**:
- Entity: `KnowledgeArticle`
- Related: `Category`, `User`, `Incident`, `Request`, `Service`

---

#### 4. Service Level Management
**ITIL Definition**: Set clear business-based targets for service performance so that delivery can be properly assessed, monitored, and managed.

**OpsIT Implementation**:

```
Key Features:
- SLA definitions (response time, resolution time)
- Priority-based SLA matrix
- Business hours vs 24/7 support
- SLA tracking per ticket
- Breach warnings (notifications before breach)
- SLA pause/resume (e.g., waiting for customer)
- Escalation rules (when SLA at risk)
- SLA reporting and dashboards
- OLA (Operational Level Agreement) support
- Metrics: SLA compliance %, Average resolution time, Breach analysis
```

**Database Mapping**:
- Entity: `SLA`, `SLAHistory`
- Related: `Incident`, `Request`, `Service`, `Priority`

**ITIL Terms**:
- SLA (Service Level Agreement) → `SLA` table
- OLA (Operational Level Agreement) → `SLA` with internal flag
- UC (Underpinning Contract) → vendor SLAs (future)

---

### Phase 2: Foundation & CMDB

#### 5. Service Configuration Management
**ITIL Definition**: Ensure that accurate and reliable information about configuration items, and relationships between them, is available when needed.

**OpsIT Implementation**:

```
Key Features:
- CMDB (Configuration Management Database)
- CI lifecycle management (Plan → Order → Deploy → Operate → Dispose)
- CI relationships (Depends On, Runs On, Supports, etc.)
- CI change tracking (audit trail)
- Impact analysis (show dependent CIs)
- CI classes and types (hierarchical)
- Asset attributes (custom per CI type)
- Integration with incidents/changes (affected CI)
- Service mapping (CIs supporting services)
- Metrics: CI accuracy, Relationship completeness, Change rate
```

**Database Mapping**:
- Entity: `ConfigurationItem`, `CIType`, `CIClass`, `CIRelationship`
- Related: `Service`, `Incident`, `Change`, `User`, `Location`

**ITIL Terms**:
- Configuration Item (CI) → `ConfigurationItem`
- CMDB → PostgreSQL database with CI tables
- Configuration Baseline → CI snapshot (future)
- Definitive Media Library (DML) → Asset attachments

---

#### 6. Service Catalog Management
**ITIL Definition**: Provide a single source of consistent information on all services and service offerings.

**OpsIT Implementation**:

```
Key Features:
- Service portfolio (all services)
- Service catalog (customer-facing services)
- Service descriptions and owners
- Service dependencies (on CIs)
- Service status (Active, Planned, Retired)
- Service hours and availability
- SLA per service
- Request catalog items linked to services
- Service hierarchy (business → technical services)
- Metrics: Service availability, Service usage, Customer satisfaction
```

**Database Mapping**:
- Entity: `Service`, `CatalogItem`
- Related: `ConfigurationItem`, `SLA`, `User`, `Group`

---

### Phase 3: Advanced ITIL Practices

#### 7. Problem Management
**ITIL Definition**: Reduce the likelihood and impact of incidents by identifying actual and potential causes of incidents, and managing workarounds and known errors.

**OpsIT Implementation**:

```
Workflow:
1. Problem Identification → 2. Problem Logging → 3. Problem Categorization →
4. Problem Investigation & Diagnosis → 5. Workaround →
6. Known Error Creation → 7. Problem Resolution → 8. Problem Closure

Key Features:
- Link multiple incidents to a problem
- Root cause analysis documentation
- Known error database
- Workaround documentation
- Problem priority and impact
- Link to changes (fixes)
- Proactive problem identification (trends)
- Metrics: Problems resolved, Known errors, Incident reduction
```

**Database Mapping**:
- Entity: `Problem` (extends `BaseTicket`)
- Related: `Incident`, `KnownError`, `Change`, `ConfigurationItem`

---

#### 8. Change Management (Change Enablement)
**ITIL Definition**: Maximize the number of successful service and product changes by ensuring risks are properly assessed, authorizing changes to proceed, and managing the change schedule.

**OpsIT Implementation**:

```
Workflow:
1. Change Request → 2. Change Assessment (risk, impact) →
3. Change Authorization (CAB approval if needed) → 4. Change Planning →
5. Change Implementation → 6. Change Review → 7. Change Closure

Change Types:
- Standard Changes (pre-approved, low risk)
- Normal Changes (requires assessment and approval)
- Emergency Changes (expedited process)

Key Features:
- Change categorization and risk assessment
- CAB (Change Advisory Board) approval workflow
- Change calendar (scheduling)
- Impact analysis (affected CIs and services)
- Implementation and backout plans
- Change freeze periods
- Change success rate tracking
- Link to incidents (caused by change)
- Metrics: Change success rate, Emergency changes %, CAB efficiency
```

**Database Mapping**:
- Entity: `Change` (extends `BaseTicket`)
- Related: `ConfigurationItem`, `Service`, `Incident`, `Problem`, `ApprovalRequest`

**ITIL Roles**:
- Change Manager → Admin managing changes
- Change Advisory Board (CAB) → Approval `Group`
- Change Authority → User/Group with approval rights

---

#### 9. Asset Management
**ITIL Definition**: Plan and manage the full lifecycle of all IT assets.

**OpsIT Implementation**:

```
Lifecycle:
Plan → Acquire → Deploy → Maintain → Dispose

Key Features:
- Hardware and software asset tracking
- Procurement tracking (PO, vendor, cost)
- License management (keys, expiry)
- Asset assignment (checkout/checkin)
- Depreciation tracking
- Warranty and maintenance tracking
- Asset disposal workflow
- Integration with CMDB (Asset → CI)
- Barcode/QR code support
- Metrics: Asset utilization, License compliance, TCO
```

**Database Mapping**:
- Entity: `Asset` (extends `ConfigurationItem`)
- Related: `User`, `Location`, `Vendor`, `PurchaseOrder`

---

#### 10. Continual Improvement
**ITIL Definition**: Align practices and services with changing business needs through ongoing improvement.

**OpsIT Implementation**:

```
Key Features:
- Built-in analytics and dashboards
- Trend analysis (incident trends, SLA performance)
- Feedback loops (user surveys, ratings)
- Process metrics (KPIs)
- Improvement suggestions (from users and agents)
- Regular service reviews
- A/B testing for workflows
- Metrics: All ITIL metrics across practices
```

---

## ITIL Metrics & Reporting in OpsIT

### Incident Management KPIs
- Mean Time to Resolve (MTTR)
- Mean Time to Respond (MTTR)
- First Contact Resolution Rate (FCR)
- Incident Volume (by category, priority, time)
- SLA Compliance %
- Backlog size
- Escalation rate
- Reopened incidents %

### Request Management KPIs
- Average Fulfillment Time
- Request Volume
- Approval Time
- SLA Compliance %
- Catalog item usage
- User satisfaction

### Problem Management KPIs
- Number of problems
- Root causes identified
- Known errors created
- Incident reduction rate
- Problem resolution time

### Change Management KPIs
- Change success rate
- Emergency changes %
- Unauthorized changes
- Average implementation time
- Failed changes (rollback rate)

### Service Level KPIs
- Overall SLA compliance %
- Average response time
- Average resolution time
- Breach reasons analysis

### CMDB KPIs
- CI accuracy rate
- Relationship completeness
- CI change rate
- Unauthorized CIs

---

## ITIL Roles in OpsIT

### Core Roles (Implemented in User/Group/Role)

1. **Service Desk Agent**
   - Handle incidents and requests
   - Log tickets
   - Basic troubleshooting
   - Escalate when needed

2. **Incident Manager**
   - Oversee incident process
   - Manage major incidents
   - Review metrics
   - Process improvement

3. **Problem Manager**
   - Investigate recurring incidents
   - Maintain known error database
   - Root cause analysis

4. **Change Manager**
   - Assess change requests
   - Schedule changes
   - Facilitate CAB
   - Review change success

5. **Service Owner**
   - Accountable for service delivery
   - Define SLAs
   - Service improvement

6. **Configuration Manager**
   - Maintain CMDB accuracy
   - Manage CI relationships
   - Audit CIs

7. **Knowledge Manager**
   - Curate knowledge base
   - Ensure article quality
   - Promote knowledge reuse

8. **End User / Customer**
   - Submit incidents and requests
   - Access self-service portal
   - Provide feedback

---

## ITIL Integration with OpsIT Features

### Portal (Self-Service)
- Incident submission (ITIL: Incident logging)
- Service catalog (ITIL: Request fulfillment)
- Knowledge base (ITIL: Knowledge management)
- Status tracking (ITIL: Transparency)
- User communication (ITIL: Keep users informed)

### Automation
- Auto-categorization (ITIL: Efficient classification)
- Auto-assignment (ITIL: Fast routing)
- SLA automation (ITIL: Service level management)
- Escalation rules (ITIL: Escalation procedures)
- Approval workflows (ITIL: Change authorization)

### Reporting
- All ITIL KPIs built-in
- Executive dashboards
- Operational reports
- Trend analysis
- Compliance reports

---

## ITIL Terminology Mapping

| ITIL Term | OpsIT Implementation |
|-----------|---------------------|
| Incident | `Incident` table |
| Service Request | `Request` table |
| Problem | `Problem` table (Phase 3) |
| Change | `Change` table (Phase 3) |
| Configuration Item (CI) | `ConfigurationItem` table |
| CMDB | PostgreSQL database |
| Service Catalog | `CatalogItem` table |
| SLA | `SLA` table |
| Known Error | `KnownError` table (linked to Problem) |
| Workaround | Field in `Problem` and `Incident` |
| Service Desk | Portal + ticketing system |
| CAB | Approval `Group` |
| KEDB (Known Error Database) | `KnownError` + `KnowledgeArticle` |
| CMS (Configuration Management System) | CMDB + CI relationships |
| DML (Definitive Media Library) | Asset attachments |

---

## Implementation Priority

### Phase 1 (MVP - 3 months)
✅ Incident Management (80% ITIL compliant)
✅ Request Fulfillment (80% ITIL compliant)
✅ Knowledge Management (basic)
✅ Service Level Management (basic SLAs)
✅ Portal (self-service)

### Phase 2 (Foundation - 3 months)
- Service Configuration Management (CMDB)
- Service Catalog Management
- Enhanced Knowledge Management
- Advanced SLAs and OLAs

### Phase 3 (Advanced - 6 months)
- Problem Management
- Change Management
- Asset Management
- Continual Improvement practices

---

## ITIL Compliance Level

**Target**: 90%+ ITIL v4 compliance for core practices

**How OpsIT ensures ITIL compliance**:
1. Built-in ITIL workflows
2. ITIL terminology throughout
3. Required fields per ITIL best practices
4. Standard ITIL reports
5. ITIL role templates
6. Documentation aligned with ITIL framework
7. Training materials reference ITIL
