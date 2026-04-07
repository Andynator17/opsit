# OpsIT - MVP Roadmap

## MVP Goal
Launch a functional ITSM platform in **3 months** with core incident and request management capabilities.

---

## MVP Scope (Phase 1 - 3 Months)

### What's IN for MVP ✅

**Core Ticket Management**
- ✅ Incident Management (create, update, assign, resolve, close)
- ✅ Request Management (create, update, approval, fulfill)
- ✅ Ticket statuses and workflow
- ✅ Priority/urgency/impact matrix
- ✅ Categories and subcategories
- ✅ Comments and work notes
- ✅ File attachments
- ✅ Assignment (to user or group)

**User Management**
- ✅ User authentication (JWT)
- ✅ Basic RBAC (Admin, Agent, End User roles)
- ✅ User profiles
- ✅ Groups/teams
- ✅ Password management

**Service Catalog**
- ✅ Basic catalog items (5-10 pre-defined)
- ✅ Request forms
- ✅ Simple approval workflow (single approver)

**Portal (Self-Service)**
- ✅ User login
- ✅ Submit incidents
- ✅ Submit requests from catalog
- ✅ View my tickets
- ✅ Add comments
- ✅ Basic knowledge base (view articles)

**SLA Management**
- ✅ Basic SLA definitions (by priority)
- ✅ SLA tracking (due date, breach warning)
- ✅ SLA breach notifications

**Dashboard**
- ✅ Agent dashboard (my tickets, team queue)
- ✅ Basic metrics (open, in progress, resolved)
- ✅ SLA compliance widget

**Notifications**
- ✅ Email notifications (ticket created, assigned, resolved)
- ✅ In-app notifications

**Search & Filter**
- ✅ Basic search (ticket number, title)
- ✅ Filter by status, priority, assigned to

**Foundation Data**
- ✅ Departments
- ✅ Locations
- ✅ Categories

**Security**
- ✅ Multi-tenancy (database isolation)
- ✅ Password hashing (Argon2)
- ✅ Basic audit logging
- ✅ HTTPS/TLS

**Deployment**
- ✅ Docker Compose for local development
- ✅ Basic Docker deployment

### What's OUT for MVP ❌ (Phase 2+)

- ❌ CMDB (Configuration Items)
- ❌ Problem Management
- ❌ Change Management
- ❌ Asset Management
- ❌ Advanced workflows (multi-level approvals)
- ❌ Knowledge base creation/editing (admin only in MVP)
- ❌ Advanced reporting (only basic dashboard)
- ❌ MFA (Multi-Factor Authentication)
- ❌ SSO/SAML integration
- ❌ API rate limiting
- ❌ Advanced SLA features (pause, business hours)
- ❌ Webhooks
- ❌ Mobile app
- ❌ Advanced search (full-text, Elasticsearch)
- ❌ Real-time collaboration (WebSockets)
- ❌ File preview
- ❌ Bulk operations
- ❌ Custom fields UI (JSONB backend exists, no UI)
- ❌ Tenant self-registration
- ❌ Billing integration

---

## Week-by-Week Plan (12 Weeks)

### Week 1-2: Project Setup & Foundation
**Backend:**
- [ ] Initialize FastAPI project structure
- [ ] Setup PostgreSQL database
- [ ] Setup Redis
- [ ] Create base models (BaseModel, database connection)
- [ ] Setup Alembic migrations
- [ ] Create initial migration (tenants, users, roles, groups)
- [ ] Implement authentication (JWT, login, refresh token)
- [ ] Setup Celery for background tasks

**Frontend:**
- [ ] Initialize React + Vite + TypeScript project
- [ ] Setup Ant Design / Shadcn UI
- [ ] Setup routing (React Router)
- [ ] Setup state management (Zustand)
- [ ] Create basic layout (Header, Sidebar, Main)
- [ ] Implement login page
- [ ] Setup API client (Axios)

**DevOps:**
- [ ] Create Docker Compose for development
- [ ] Setup .env configuration
- [ ] Create seed data scripts

**Deliverable:** User can login and see empty dashboard

---

### Week 3-4: User & Group Management
**Backend:**
- [ ] User CRUD endpoints
- [ ] Group CRUD endpoints
- [ ] Department and Location tables
- [ ] Role-based permissions
- [ ] Current user endpoint

**Frontend:**
- [ ] User list page
- [ ] User create/edit form
- [ ] Group management page
- [ ] User profile page

**Deliverable:** Admin can create users and groups

---

### Week 5-7: Incident Management
**Backend:**
- [ ] Incident model and migration
- [ ] Category model
- [ ] Incident CRUD endpoints
- [ ] Ticket number generation
- [ ] Status workflow
- [ ] Comment model and endpoints
- [ ] Attachment model and endpoints (S3 or local storage)
- [ ] Assignment logic
- [ ] Email notifications (incident created, assigned)

**Frontend:**
- [ ] Incident list page (with filters)
- [ ] Incident detail page
- [ ] Create incident page/modal
- [ ] Edit incident (status, assignment, priority)
- [ ] Comments section
- [ ] File upload component
- [ ] Agent dashboard (my incidents, team queue)

**Deliverable:** Full incident lifecycle works end-to-end

---

### Week 8-9: Request Management & Service Catalog
**Backend:**
- [ ] Request model and migration
- [ ] Catalog item model
- [ ] Request CRUD endpoints
- [ ] Approval request model
- [ ] Simple approval workflow
- [ ] Approval endpoints (approve/reject)

**Frontend:**
- [ ] Service catalog page
- [ ] Request submission form (dynamic based on catalog item)
- [ ] Request list page
- [ ] Request detail page
- [ ] Approval interface (for approvers)
- [ ] My requests page (for end users)

**Deliverable:** Users can submit requests and get approvals

---

### Week 10: SLA & Dashboard
**Backend:**
- [ ] SLA model and migration
- [ ] SLA calculation logic
- [ ] SLA tracking (due dates)
- [ ] SLA breach detection (Celery task)
- [ ] Dashboard summary endpoint
- [ ] Basic metrics endpoints

**Frontend:**
- [ ] Dashboard widgets (ticket counts, SLA compliance)
- [ ] SLA indicator on tickets
- [ ] Admin SLA configuration page

**Deliverable:** SLAs are tracked and displayed

---

### Week 11: Portal (Self-Service)
**Backend:**
- [ ] Public/portal endpoints (no admin access)
- [ ] Knowledge article model (read-only for MVP)
- [ ] Search endpoint

**Frontend:**
- [ ] Portal layout (different from agent interface)
- [ ] Portal home page
- [ ] Submit incident (simplified form)
- [ ] Submit request (catalog)
- [ ] My tickets page
- [ ] Knowledge base search and view

**Deliverable:** End users can self-service via portal

---

### Week 12: Testing, Bug Fixes, Deployment Prep
- [ ] End-to-end testing
- [ ] Security audit (OWASP checklist)
- [ ] Performance testing
- [ ] Bug fixes
- [ ] Documentation (user guide, admin guide)
- [ ] Deployment scripts
- [ ] Production Docker Compose
- [ ] Basic monitoring setup

**Deliverable:** MVP ready for production deployment

---

## MVP Feature Details

### 1. Incident Management (Core)

**User Stories:**
- As an **end user**, I can create an incident describing my issue
- As an **agent**, I can view all open incidents in my queue
- As an **agent**, I can assign incidents to myself or other agents
- As an **agent**, I can update incident status (In Progress, Resolved, Closed)
- As an **agent**, I can add work notes and customer notes
- As an **agent**, I can attach files (screenshots, logs)
- As a **manager**, I can see all incidents for my team

**Screens:**
1. Incident List (filterable, sortable)
2. Incident Detail (all fields, comments, history)
3. Create Incident (form)
4. Quick Edit (modal for status/assignment)

**API Endpoints:**
```
GET    /api/v1/incidents
POST   /api/v1/incidents
GET    /api/v1/incidents/{id}
PATCH  /api/v1/incidents/{id}
POST   /api/v1/incidents/{id}/comments
POST   /api/v1/incidents/{id}/attachments
POST   /api/v1/incidents/{id}/assign
```

**ITIL Compliance:**
- Incident logging ✅
- Categorization ✅
- Prioritization ✅
- Assignment ✅
- Resolution ✅
- Closure ✅

---

### 2. Request Management

**User Stories:**
- As an **end user**, I can browse the service catalog
- As an **end user**, I can submit a request for a catalog item
- As an **approver**, I can approve or reject requests
- As an **agent**, I can fulfill approved requests
- As an **end user**, I can track my request status

**Screens:**
1. Service Catalog (grid/list of items)
2. Catalog Item Detail + Request Form
3. Request List
4. Request Detail
5. Approval Interface

**API Endpoints:**
```
GET    /api/v1/catalog/items
POST   /api/v1/requests
GET    /api/v1/requests
GET    /api/v1/requests/{id}
POST   /api/v1/requests/{id}/approve
POST   /api/v1/requests/{id}/reject
```

---

### 3. Dashboard

**Widgets:**
1. **My Tickets** - Tickets assigned to me
2. **Team Queue** - Unassigned tickets for my group
3. **Ticket Stats** - Open, In Progress, Resolved (today)
4. **SLA Compliance** - Percentage, breached tickets
5. **Recent Activity** - Latest ticket updates

**For End Users (Portal Dashboard):**
1. **My Open Tickets**
2. **Quick Actions** (Create Incident, Browse Catalog)
3. **Knowledge Base Search**

---

### 4. Portal (Self-Service)

**Pages:**
1. Home (quick actions, status)
2. Create Incident
3. Service Catalog
4. My Tickets
5. Ticket Detail
6. Knowledge Base

**Features:**
- Simplified UI (no admin features)
- Mobile responsive
- Quick ticket creation
- Real-time status updates (polling)

---

### 5. SLA Management

**MVP SLA Features:**
- Define SLA by priority (critical: 1h, high: 4h, medium: 8h, low: 24h)
- Calculate due date on ticket creation
- Display time remaining on ticket
- Email notification when SLA at risk (80% consumed)
- Email notification on SLA breach
- Dashboard widget showing compliance

**Not in MVP:**
- Business hours calculation
- SLA pause/resume
- Multiple SLAs per ticket type
- OLAs (Operational Level Agreements)

---

## Technology Stack (Confirmed)

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **Password**: Argon2 (passlib)
- **Tasks**: Celery
- **Cache**: Redis
- **Email**: SMTP (via aiosmtplib)
- **Validation**: Pydantic v2

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build**: Vite
- **UI Library**: Ant Design or Shadcn/UI
- **State**: Zustand
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod
- **API**: Axios + TanStack Query
- **Charts**: Recharts

### DevOps
- **Containers**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: (Phase 2) Prometheus + Grafana
- **Logging**: (Phase 2) ELK Stack

---

## Success Metrics for MVP

### Functional Metrics
- ✅ User can create and resolve an incident in < 2 minutes
- ✅ 100% of ITIL Incident Management workflow implemented
- ✅ 100% of ITIL Request Fulfillment workflow implemented
- ✅ SLA tracking accuracy: 99%+
- ✅ Zero security vulnerabilities (OWASP Top 10)

### Performance Metrics
- ✅ Page load time: < 2 seconds
- ✅ API response time: < 200ms (p95)
- ✅ Support 100 concurrent users
- ✅ Database queries < 100ms

### Quality Metrics
- ✅ 80%+ test coverage (backend)
- ✅ 60%+ test coverage (frontend)
- ✅ Zero critical bugs
- ✅ < 5 high-priority bugs at launch

---

## Post-MVP Roadmap (Phase 2 - Months 4-6)

### Phase 2 Features
1. **CMDB (Configuration Management Database)**
   - CI types and classes
   - CI relationships
   - Impact analysis
   - Link incidents/requests to CIs

2. **Advanced Workflows**
   - Multi-level approvals
   - Conditional routing
   - Escalation rules
   - Auto-assignment based on rules

3. **Knowledge Management**
   - Article creation and editing (rich text)
   - Article lifecycle (draft → review → published)
   - Article versioning
   - AI-suggested articles during ticket creation

4. **Advanced Reporting**
   - Custom reports
   - Report scheduler
   - Export to PDF/Excel
   - Trend analysis

5. **SSO Integration**
   - SAML 2.0
   - Azure AD / Okta
   - LDAP/Active Directory

6. **Real-time Features**
   - WebSocket for live updates
   - Typing indicators
   - Real-time dashboard

7. **Mobile Responsiveness**
   - Optimized mobile UI
   - Progressive Web App (PWA)

---

## Phase 3 - Months 7-12

### Enterprise Features
1. **Problem Management**
2. **Change Management**
3. **Asset Management**
4. **Advanced SLA** (business hours, pause/resume, OLAs)
5. **Multi-language Support** (i18n)
6. **Advanced Security** (MFA, IP whitelisting, session management)
7. **API Management** (rate limiting, webhooks, API keys)
8. **Integrations** (Slack, MS Teams, Jira, etc.)
9. **Automation Engine** (scriptable workflows)
10. **BI Dashboard** (advanced analytics)

---

## Team Composition (Recommended)

### For MVP (3 months)
- **1 Backend Developer** (Python/FastAPI)
- **1 Frontend Developer** (React/TypeScript)
- **0.5 DevOps Engineer** (Docker, deployment)
- **0.5 QA Engineer** (testing)
- **0.5 UI/UX Designer** (if not using standard component library)

### Total: ~3.5 FTE

**Alternative (Solo Developer):**
- 6 months for MVP
- Focus on backend first (weeks 1-8)
- Then frontend (weeks 9-16)
- Integration and testing (weeks 17-24)

---

## Risk Mitigation

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Database performance issues | Early performance testing, proper indexing, use materialized views |
| Multi-tenancy data leakage | Row-level security, thorough testing, security audit |
| SLA calculation accuracy | Comprehensive unit tests, use proven algorithms |
| Email delivery issues | Use reliable SMTP provider (SendGrid, AWS SES), retry logic |
| File storage costs | Implement size limits, cleanup policies, compression |

### Project Risks
| Risk | Mitigation |
|------|------------|
| Scope creep | Strict MVP definition, feature freeze after week 10 |
| Integration complexity | Minimize external dependencies in MVP |
| Testing time underestimated | Start testing from week 1, continuous integration |
| Deployment issues | Test deployment early (week 8), use proven tools |

---

## Launch Checklist

### Pre-Launch (Week 11-12)
- [ ] All MVP features complete and tested
- [ ] Security audit completed (OWASP Top 10)
- [ ] Performance testing passed
- [ ] Backup and restore tested
- [ ] Monitoring and logging configured
- [ ] User documentation written
- [ ] Admin documentation written
- [ ] Support procedures defined
- [ ] Incident response plan documented
- [ ] GDPR compliance verified
- [ ] Terms of Service and Privacy Policy published

### Launch Day
- [ ] Deploy to production
- [ ] Smoke tests passed
- [ ] Monitor error logs
- [ ] Monitor performance metrics
- [ ] Customer support ready
- [ ] Announcement sent

### Post-Launch (Week 1-2)
- [ ] Gather user feedback
- [ ] Fix critical bugs (if any)
- [ ] Monitor usage metrics
- [ ] Plan Phase 2 features

---

## Budget Estimate (MVP)

### Development Costs (3 months)
- Backend Developer: €60k/year × 3 months = €15k
- Frontend Developer: €60k/year × 3 months = €15k
- DevOps Engineer: €70k/year × 1.5 months = €8.75k
- QA Engineer: €50k/year × 1.5 months = €6.25k
- **Total Development**: ~€45k

### Infrastructure Costs (Monthly)
- Database (managed PostgreSQL): €100/month
- App hosting (2 containers): €100/month
- Redis (managed): €30/month
- Email (SendGrid): €15/month
- File storage (S3): €20/month
- Domain & SSL: €10/month
- **Total Infrastructure**: ~€275/month

### Tools & Services
- GitHub: Free (or €7/user/month)
- Sentry (error tracking): Free tier
- Figma (design): Free tier
- **Total Tools**: ~€0-20/month

**Total MVP Cost**: ~€50k (development + 3 months infra)

---

## Conclusion

This MVP roadmap provides a clear path to launching OpsIT in 3 months with core ITSM functionality:
- ✅ Incident Management (ITIL compliant)
- ✅ Request Management (ITIL compliant)
- ✅ Service Catalog
- ✅ SLA Tracking
- ✅ Self-Service Portal
- ✅ Basic Dashboards

**Next Steps:**
1. Finalize team composition
2. Setup development environment (Week 1)
3. Start backend foundation (Week 1-2)
4. Weekly demos to stakeholders
5. Adjust plan based on progress

**Success Criteria:**
- Ship on time (12 weeks)
- Meet all MVP requirements
- Zero critical bugs
- ITIL compliant
- ISO 27001 ready
- Positive early user feedback

Let's build OpsIT! 🚀
