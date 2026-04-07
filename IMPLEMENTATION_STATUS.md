# OpsIT - Implementation Status

> Last updated: 2026-02-11

## Architecture Overview

```
Frontend (React 18 + TS + Ant Design)     Backend (FastAPI + SQLAlchemy 2.0 async)
┌─────────────────────────────────┐       ┌──────────────────────────────────┐
│  DashboardLayout                │       │  main.py (FastAPI app)           │
│  ├── Header (Search, Theme,     │       │  ├── CORS middleware             │
│  │    Notifications, User)      │  API  │  ├── 16 API route modules        │
│  ├── Sidebar (Menu navigation)  │◄─────►│  ├── 18 SQLAlchemy models        │
│  └── TabManager                 │  JWT  │  ├── 18 Pydantic schemas         │
│       ├── Dashboard             │       │  └── core/ (auth, db, deps)      │
│       ├── TaskList + TaskForm   │       │                                  │
│       ├── UserList + UserForm   │       │  PostgreSQL 16                   │
│       ├── CompanyList + Form    │       │  ├── Multi-tenant (tenant_id)    │
│       ├── DeptList + Form       │       │  ├── 12 Alembic migrations       │
│       ├── LocationList + Form   │       │  └── Row-level security          │
│       ├── SupportGroupList+Form │       │                                  │
│       ├── PermGroupList + Form  │       │  Auth: JWT + Argon2id            │
│       └── RoleList + RoleForm   │       │  RBAC: Roles + Permission Groups │
└─────────────────────────────────┘       └──────────────────────────────────┘
```

---

## Implemented Features

### Authentication & Authorization
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Login (email/password) | `auth.py` | `AuthContext.tsx`, `Login.tsx` | Done |
| JWT access + refresh tokens | `security.py` | `api.ts` (interceptor) | Done |
| Argon2id password hashing | `security.py` | - | Done |
| Protected routes | `dependencies.py` | `ProtectedRoute.tsx` | Done |
| Admin-only endpoints | `get_current_admin_user` | - | Done |
| Roles (module/action permissions) | `roles.py` | `RoleList.tsx`, `RoleForm.tsx` | Done |
| Permission Groups (role bundles) | `permission_groups.py` | `PermissionGroupList/Form.tsx` | Done |
| Permission checking decorator | `permissions.py` | - | Done |

### Ticket Management (ITIL)
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Unified Task table (all ticket types) | `task.py` model | `TaskList.tsx`, `TaskForm.tsx` | Done |
| Incident (INC) lifecycle | `tasks.py` API | Full form with workflow | Done |
| Request (REQ) lifecycle | `tasks.py` API | Full form with workflow | Done |
| Change (CHG) lifecycle | `tasks.py` API | Full form with workflow | Done |
| Problem (PRB) lifecycle | `tasks.py` API | Full form with workflow | Done |
| Task (TSK) lifecycle | `tasks.py` API | Full form with workflow | Done |
| Approval (APR) lifecycle | `tasks.py` API | Full form with workflow | Done |
| Auto ticket numbering (INC000001) | `tasks.py` create | Displayed in header | Done |
| Priority matrix (urgency x impact) | `Task.calculate_priority` | Auto-calculated in form | Done |
| Status workflow (New→Assigned→...) | assign/resolve/close endpoints | Status action buttons | Done |
| Work Notes (internal) | JSONB field | Tab with add/display | Done |
| Comments (public) | JSONB field | Tab with add/display | Done |
| Audit Trail (Work Log) | `audit_log.py` model + API | Timeline in Work Log tab | Done |
| Field-level audit with name resolution | `_resolve_display_name()` | Human-readable field labels | Done |
| File Attachments | `attachments.py` API + uploads/ | Upload button + file list | Done |
| Assignment (user + group) | assign endpoint | Group→member dropdowns | Done |
| Reassignment tracking | `reassignment_count` field | Displayed in form | Done |
| Ticket search (number or text) | `search` query param | Header search bar | Done |
| Filtered lists per ticket type | `sys_class_name` filter | Sidebar menu items | Done |
| My groups filter | `assigned_to_my_groups` | Toggle in TaskList | Done |

### Organization Structure
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Companies (CRUD) | `companies.py` | `CompanyList.tsx`, `CompanyForm.tsx` | Done |
| Main IT Company flag | `is_main_it_company` field | Switch in CompanyForm | Done |
| Departments (CRUD) | `departments.py` | `DepartmentList.tsx`, `DepartmentForm.tsx` | Done |
| Dept hierarchy (parent_department) | `parent_department_id` FK | Select in form | Done |
| Dept manager assignment | `manager_id` FK | User select in form | Done |
| Locations (CRUD) | `locations.py` | `LocationList.tsx`, `LocationForm.tsx` | Done |
| User→Department (FK) | `department_id` on User | Select dropdown in UserForm | Done |
| User→Location (FK) | `location_id` on User | Select dropdown in UserForm | Done |
| User→Company (FK) | `primary_company_id` on User | Select dropdown in UserForm | Done |

### User Management
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| User CRUD | `users.py` | `UserList.tsx`, `UserForm.tsx` | Done |
| Extended user fields | salutation, title, gender, phones | Full form with all fields | Done |
| User types (admin/agent/user) | `user_type` field | Select + Tag display | Done |
| VIP flag | `is_vip` field | Switch in form | Done |
| Support group membership | via `group_members` table | Add/remove in UserForm | Done |
| Permission group membership | via `permission_group_members` | Add/remove in UserForm | Done |

### Support Groups
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Support Group CRUD | `support_groups.py` | `SupportGroupList/Form.tsx` | Done |
| Group types (support/ops/dev/mgmt) | `group_type` field | Select + Tag display | Done |
| Member management | add/remove members endpoints | Add/remove in form | Done |
| Group→Company association | `company_id` FK | Company select | Done |
| Group manager | `manager_id` FK | User select | Done |

### Dashboard & UI
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Dashboard statistics | `dashboard.py` API | `Dashboard.tsx` | Done |
| Open tickets by priority | Aggregation query | Stat cards | Done |
| Tickets by status chart | Aggregation query | Stat display | Done |
| Recent tickets list | Latest tasks query | Table with links | Done |
| Tab-based navigation | - | `TabContext.tsx`, `TabManager.tsx` | Done |
| Nested sub-tabs (list→form) | - | Parent/child tab system | Done |
| Tab persistence (localStorage) | - | `tabContentFactory.tsx` | Done |
| Dark mode | - | `ThemeContext.tsx` | Done |
| Header search bar | - | `DashboardLayout.tsx` | Done |
| Notification bell (placeholder) | - | Badge + icon in header | Done |
| Sidebar with grouped sections | - | Fulfillment/Foundation/System | Done |

### Categories
| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Hierarchical categories | `categories.py` | Used in TaskForm selects | Done |
| Category→Subcategory | parent_id FK | Cascading selects | Done |

---

## Database Schema (12 Migrations)

| # | Migration | Tables/Changes |
|---|-----------|---------------|
| 1 | `adf010f78e12` | tenants, companies, users (initial) |
| 2 | `72616e239316` | incidents table |
| 3 | `12ac07208747` | requests table |
| 4 | `4b018309ada7` | categories, support_groups, group_members |
| 5 | `5c2d3a7b9e14` | roles, permissions, permission_groups, permission_group_members, permission_group_roles |
| 6 | `6d7e8f9a0b12` | Extended user fields (salutation, title, phones, etc.) |
| 7 | `7e8f9a0b13c2` | user_type field |
| 8 | `a12adab4151a` | Incident user fields (opened_by, caller, affected_user) |
| 9 | `e5b6eb413529` | tasks table (unified ticket system) |
| 10 | `73ec03b5daa4` | work_notes + comments JSONB on tasks |
| 11 | `2c884bd4a9f5` | attachments table |
| 12 | `1eac3087dfe2` | audit_logs, notifications, departments, locations + user FKs |

---

## API Endpoints Summary

| Module | Prefix | Key Endpoints |
|--------|--------|--------------|
| `auth.py` | `/auth` | POST login, POST refresh |
| `users.py` | `/users` | CRUD + me endpoint |
| `tasks.py` | `/tasks` | CRUD + assign/resolve/close |
| `incidents.py` | `/incidents` | Legacy CRUD (pre-unified) |
| `requests.py` | `/requests` | Legacy CRUD (pre-unified) |
| `companies.py` | `/companies` | CRUD |
| `departments.py` | `/departments` | CRUD |
| `locations.py` | `/locations` | CRUD |
| `support_groups.py` | `/support-groups` | CRUD + member management |
| `permission_groups.py` | `/permission-groups` | CRUD + role/member management |
| `roles.py` | `/roles` | CRUD + permissions |
| `categories.py` | `/categories` | CRUD (hierarchical) |
| `attachments.py` | `/attachments` | Upload/download/list/delete |
| `audit_logs.py` | `/tasks/{id}/audit-logs` | List audit entries |
| `dashboard.py` | `/dashboard` | Stats + aggregations |

---

## Not Yet Implemented (Roadmap)

### Phase 2 (Next)
- [ ] CMDB (Configuration Management Database)
- [ ] Knowledge Base (articles, search)
- [ ] SLA Engine (breach detection, escalation)
- [ ] Email notifications (connect notification table to SMTP)
- [ ] SSO integration (SAML/OIDC)
- [ ] Advanced workflows (approval chains)
- [ ] Reporting & export (PDF/Excel)
- [ ] User avatar upload

### Phase 3 (Later)
- [ ] Multi-language support (i18n)
- [ ] API webhooks
- [ ] Self-service portal (end-user view)
- [ ] Calendar/scheduling integration
- [ ] Mobile responsive improvements
- [ ] Bulk operations on tickets
- [ ] Custom fields UI builder
- [ ] Docker Compose production setup

---

## Running the Project

```bash
# Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm run dev

# Default admin: admin@opsit.com / Admin123!
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/v1/docs (if enabled)
```
