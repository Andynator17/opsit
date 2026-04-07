# OpsIT – Feature-Analyse (Stand 2026-04-07)

Quelle: Code in `backend/app/api/v1/`, `backend/app/models/`, `frontend/src/`. MD-Docs im Root nur als Kontext.

Reifegrad-Skala: **Stub** · **Basic** · **Funktional** · **Vollständig**

## 1. Authentifizierung & Session

JWT mit Access- und Refresh-Token, bcrypt-Passwörter, Login-Zähler im User-Modell.

| Aspekt | Details |
|---|---|
| Backend | [auth.py](../backend/app/api/v1/auth.py) – `POST /auth/login`, `POST /auth/register`, `GET /auth/me` |
| Core | [security.py](../backend/app/core/security.py), [dependencies.py](../backend/app/core/dependencies.py) |
| Modelle | [user.py](../backend/app/models/user.py) |
| Schemas | [auth.py](../backend/app/schemas/auth.py) |
| Frontend | [Login.tsx](../frontend/src/pages/Login.tsx), [AuthContext.tsx](../frontend/src/context/AuthContext.tsx), [auth.service.ts](../frontend/src/services/auth.service.ts), [api.ts](../frontend/src/services/api.ts) |
| Reifegrad | **Funktional** |

**Lücken:** `POST /auth/refresh` wird vom Frontend-Interceptor aufgerufen, aber im Backend **nicht implementiert**. `mfa_enabled`, `locked_until`, `failed_login_attempts` werden nicht erzwungen. Kein Logout-Endpoint. `POST /auth/register` wählt ersten Tenant automatisch.

## 2. RBAC – Rollen, Permission-Groups, Support-Groups

| Aspekt | Details |
|---|---|
| Backend | [roles.py](../backend/app/api/v1/roles.py), [permission_groups.py](../backend/app/api/v1/permission_groups.py), [support_groups.py](../backend/app/api/v1/support_groups.py) |
| Modelle | [role.py](../backend/app/models/role.py), [permission_group.py](../backend/app/models/permission_group.py), [support_group.py](../backend/app/models/support_group.py) |
| Schemas | [role.py](../backend/app/schemas/role.py), [permission_group.py](../backend/app/schemas/permission_group.py), [support_group.py](../backend/app/schemas/support_group.py) |
| Core | [permissions.py](../backend/app/core/permissions.py), [seed_roles.py](../backend/app/core/seed_roles.py) |
| Frontend | Generisches DynamicList/DynamicForm – kein spezielles UI |
| Reifegrad | **Funktional** (CRUD/Datenmodell), **aber Enforcement fehlt** |

Endpunkte: `/roles/` (GET/POST/PATCH/DELETE), `/permission-groups/` mit `members` und `roles` Sub-Ressourcen, `/support-groups/` mit `members` Sub-Ressource (inkl. `is_team_lead`).

**Größte Lücke (systemweit):** Die Autorisierung erfolgt in allen Endpunkten nur über die Boolean-Flags `is_admin`/`is_support_agent`. Der Modul/Level-Rollenkatalog und die Permission-Strings aus `Role.permissions` werden **an keiner Stelle** abgefragt. RBAC-Schema vorhanden, aber nicht enforcement-wirksam.

## 3. Multi-Tenancy & Multi-Company

| Aspekt | Details |
|---|---|
| Backend | [companies.py](../backend/app/api/v1/companies.py), [users.py](../backend/app/api/v1/users.py) |
| Modelle | [tenant.py](../backend/app/models/tenant.py), [company.py](../backend/app/models/company.py), [user.py](../backend/app/models/user.py), [base.py](../backend/app/models/base.py) |
| Schemas | [tenant.py](../backend/app/schemas/tenant.py), [company.py](../backend/app/schemas/company.py), [user.py](../backend/app/schemas/user.py) |
| Reifegrad | **Funktional** |

`company_type`, `parent_company_id`, `is_main_it_company` vorhanden; Task-Felder `caller_company_id`/`affected_user_company_id` im Modell, aber nicht in Schemas befüllt. Kein Tenant-CRUD-Endpunkt, keine DB-level RLS.

## 4. Zentrales Task-Modell

Alle Ticket-Typen (incident, request, change, problem, task, request_item, approval) via eine einzige Tabelle `tasks` mit `sys_class_name` (ServiceNow-Pattern). Nummerierung INC/REQ/CHG/PRB/TASK/RITM/APPR. Priority-Matrix aus Urgency × Impact.

| Aspekt | Details |
|---|---|
| Backend | [tasks.py](../backend/app/api/v1/tasks.py) |
| Modell | [task.py](../backend/app/models/task.py) |
| Schemas | [task.py](../backend/app/schemas/task.py) |
| Rule Engine | [rule_engine.py](../backend/app/core/rule_engine.py) – Hooks in Create/Update |
| Frontend-Liste | [DynamicList.tsx](../frontend/src/components/dynamic/DynamicList.tsx) + [tableRegistry.ts](../frontend/src/config/tableRegistry.ts) |
| Frontend-Form | [DynamicForm.tsx](../frontend/src/components/dynamic/DynamicForm.tsx) |
| Sections | [StatusWorkflow.tsx](../frontend/src/components/dynamic/sections/StatusWorkflow.tsx), [AttachmentSection.tsx](../frontend/src/components/dynamic/sections/AttachmentSection.tsx), [ActivitySection.tsx](../frontend/src/components/dynamic/sections/ActivitySection.tsx) |
| Service | [record.service.ts](../frontend/src/services/record.service.ts) |
| Reifegrad | **Funktional → Vollständig** |

Endpunkte: `POST/GET /tasks/`, `GET/PUT/DELETE /tasks/{id}`, `POST /tasks/{id}/assign|resolve|close`. Filter: `sys_class_name`, `status`, `priority`, `assigned_to_me`, `assigned_to_my_groups`, `caller_id`, `affected_user_id`, `company_id`, `search`. Audit-Log pro Feld mit UUID→Anzeigename-Resolution. Default-Gruppe `Servicedesk`.

**Lücken:** Kein Approval-Flow (`approve`/`reject`) im Task-Router. `sla_target_*` und `sla_breach` werden nirgends gesetzt. `parent_task_id` kaum genutzt. `comments`/`work_notes` nur via direkter JSON-Manipulation in `PUT /tasks/{id}`. `reassignment_count` nur im `/assign`-Endpoint aktualisiert.

## 5. Legacy Incident- und Request-Module

[incidents.py](../backend/app/api/v1/incidents.py) und [requests.py](../backend/app/api/v1/requests.py) enthalten vollständige spezifische APIs (CRUD, assign, resolve, close, approve, reject, fulfill) gegen separate Modelle [incident.py](../backend/app/models/incident.py), [request.py](../backend/app/models/request.py).

**Beide Router werden in [main.py](../backend/app/main.py) NICHT registriert** – nur `tasks.router` ist aktiv. Dead Code aus der Prä-Task-Migration. Der einzige echte Approval-Workflow (`/approve`, `/reject`, `/fulfill`) lebt hier und fehlt im Task-Modell.

Reifegrad: **Funktional, aber DEAD**.

## 6. Attachments

| Aspekt | Details |
|---|---|
| Backend | [attachments.py](../backend/app/api/v1/attachments.py) – `POST/GET/DELETE /tasks/{task_id}/attachments/`, `GET /tasks/{task_id}/attachments/{id}/download` |
| Modell | [attachment.py](../backend/app/models/attachment.py) |
| Schemas | [attachment.py](../backend/app/schemas/attachment.py) |
| Frontend | [AttachmentSection.tsx](../frontend/src/components/dynamic/sections/AttachmentSection.tsx), [attachment.service.ts](../frontend/src/services/attachment.service.ts) |
| Reifegrad | **Funktional** |

MIME-Whitelist, Size-Limit, tenant-spezifische Upload-Dirs, Soft-Delete. Keine Virenscanner-Anbindung, keine signierten Download-URLs, nur auf Tasks anwendbar.

## 7. Audit-Log

Feldgranulare History pro Task, automatisch in [tasks.py](../backend/app/api/v1/tasks.py) beschrieben.

| Aspekt | Details |
|---|---|
| Backend | [audit_logs.py](../backend/app/api/v1/audit_logs.py) – `GET /tasks/{task_id}/audit-logs/` |
| Modell | [audit_log.py](../backend/app/models/audit_log.py) |
| Schemas | [audit_log.py](../backend/app/schemas/audit_log.py) |
| Frontend | [ActivitySection.tsx](../frontend/src/components/dynamic/sections/ActivitySection.tsx), [audit.service.ts](../frontend/src/services/audit.service.ts) |
| Reifegrad | **Funktional** |

**Lücken:** Nur `tasks`-Tabelle wird auditiert; User/Company/Role/SupportGroup-Änderungen nicht. Keine Filter/Pagination, kein zentraler `/audit-logs/`-Endpoint.

## 8. Kategorien

| Aspekt | Details |
|---|---|
| Backend | [categories.py](../backend/app/api/v1/categories.py), zusätzlich `GET /portal/me/categories` |
| Modell | [category.py](../backend/app/models/category.py) |
| Schemas | [category.py](../backend/app/schemas/category.py) |
| Reifegrad | **Basic** |

Hierarchisch mit `parent_category_id`, `level`, `category_type`, Icon/Farbe. **Lücke:** `task.category` ist ein String ohne FK – die Tabelle ist nur Stammdaten-Referenz, keine echte Zuordnung.

## 9. Foundation Data – Departments, Locations

| Aspekt | Details |
|---|---|
| Backend | [departments.py](../backend/app/api/v1/departments.py), [locations.py](../backend/app/api/v1/locations.py) |
| Modelle | [department.py](../backend/app/models/department.py), [location.py](../backend/app/models/location.py) |
| Schemas | [department.py](../backend/app/schemas/department.py), [location.py](../backend/app/schemas/location.py) |
| Reifegrad | **Basic** |

**Lücke:** Auf `users.department`/`users.location` existieren parallel String-Felder neben den FK-Spalten (doppelte Wahrheit). Keine Auswirkung auf Routing.

## 10. Dashboard & Agent-Konsole

| Aspekt | Details |
|---|---|
| Backend | [dashboard.py](../backend/app/api/v1/dashboard.py) – `GET /dashboard/stats`, `GET /dashboard/stats/agent`, `GET /dashboard/overview` |
| Schemas | Inline + [dashboard.py](../backend/app/schemas/dashboard.py) |
| Frontend | [Dashboard.tsx](../frontend/src/pages/Dashboard.tsx) |
| Reifegrad | **Funktional** |

Features: Status-gegliederte Counts, "meine offenen Tickets", Agent-Metriken (unassigned incidents, SLA-Breach, per-Gruppe), Overview-Console. **Lücken:** SLA-Breach immer 0 (Ziele werden nicht gesetzt); keine Charts/Zeitreihen; "Pending Approvals" zählt nur `sys_class_name=="approval"`.

## 11. Self-Service-Portal (End-User)

| Aspekt | Details |
|---|---|
| Backend | [portal_me.py](../backend/app/api/v1/portal_me.py) |
| Schemas | [portal.py](../backend/app/schemas/portal.py) |
| Frontend-Layout | [PortalLayout.tsx](../frontend/src/components/PortalLayout.tsx) |
| Pages | [PortalOverview.tsx](../frontend/src/pages/portal/PortalOverview.tsx), [PortalTickets.tsx](../frontend/src/pages/portal/PortalTickets.tsx), [PortalTicketDetail.tsx](../frontend/src/pages/portal/PortalTicketDetail.tsx), [PortalNewTicket.tsx](../frontend/src/pages/portal/PortalNewTicket.tsx), [PortalProfile.tsx](../frontend/src/pages/portal/PortalProfile.tsx) |
| Service | [portal.service.ts](../frontend/src/services/portal.service.ts) |
| Reifegrad | **Funktional** |

Endpunkte: `GET /portal/me/stats`, `GET /portal/me/tickets`, `GET /portal/me/ticket/{id}`, `POST /portal/me/tickets` (auto `channel=portal`), `POST /portal/me/ticket/{id}/comments`, `GET /portal/me/categories`.

**Lücken:** Autorisierung nur über `caller_id == user` (requested_for wird nicht beachtet). Keine Attachment-Uploads im Portal. Keine Approval-Aktionen. Kein Self-Cancel.

## 12. Portal-Konfiguration (Admin)

| Aspekt | Details |
|---|---|
| Backend | [portals.py](../backend/app/api/v1/portals.py) – Admin-CRUD + `GET /portals/my`, `GET /portals/by-slug/{slug}` |
| Modell | [portal.py](../backend/app/models/portal.py) |
| Schemas | [portal.py](../backend/app/schemas/portal.py) |
| Reifegrad | **Basic** |

Audience `internal`/`company`/`external`, Branding, `enabled_modules`, `visible_categories`. **Lücke:** Kein Registry-Eintrag im Agent-Frontend (nur via API pflegbar). PortalKnowledge/PortalServices ignorieren `enabled_modules`.

## 13. Dynamic Forms / Metadata-System (sys_*)

ServiceNow-ähnliches Metadaten-Framework zur Laufzeit-Konfiguration. Fast alle Agent-Bildschirme rendern sich aus diesen Metadaten.

| Aspekt | Details |
|---|---|
| Backend | [sys_metadata.py](../backend/app/api/v1/sys_metadata.py) (~1450 LoC) |
| Modelle | [sys_db_object.py](../backend/app/models/sys_db_object.py), [sys_dictionary.py](../backend/app/models/sys_dictionary.py), [sys_choice.py](../backend/app/models/sys_choice.py), [sys_ui_view.py](../backend/app/models/sys_ui_view.py), [sys_ui_section.py](../backend/app/models/sys_ui_section.py), [sys_ui_element.py](../backend/app/models/sys_ui_element.py), [sys_ui_list.py](../backend/app/models/sys_ui_list.py), [sys_relationship.py](../backend/app/models/sys_relationship.py), [sys_ui_related_list.py](../backend/app/models/sys_ui_related_list.py) |
| Schemas | [sys_metadata.py](../backend/app/schemas/sys_metadata.py) |
| Frontend-Hook | [useTableMetadata.ts](../frontend/src/hooks/useTableMetadata.ts) |
| Service | [metadata.service.ts](../frontend/src/services/metadata.service.ts) |
| Rendering | [DynamicList.tsx](../frontend/src/components/dynamic/DynamicList.tsx), [DynamicForm.tsx](../frontend/src/components/dynamic/DynamicForm.tsx), [fields/](../frontend/src/components/dynamic/fields/) |
| Reifegrad | **Funktional** – größtes Feature des Projekts |

Endpunkte: CRUD auf `/sys/tables|dictionary|choices|views|sections|elements|list-columns|relationships|related-lists/` sowie aggregierende GETs `/sys/metadata/{table_name}`, `/sys/form-layout/{table_name}`, `/sys/list-layout/{table_name}` mit Super-Class-Chain und `sys_class_name`-Filter.

**Lücken:** Kein Admin-UI zum Editieren der Metadaten. Super-Class-Traversal ohne Tiefenlimit. Tenant-Filter akzeptiert globale Records (`tenant_id IS NULL`) gleichberechtigt – Overrides nicht priorisiert. `SysUiRelatedList` im Frontend nur rudimentär gerendert.

## 14. Server Scripts (Business Rules)

Deklarative Regel-Engine ohne `eval`/`exec`: JSON-Conditions und JSON-Actions, aufgerufen aus `create_task`/`update_task`.

| Aspekt | Details |
|---|---|
| Backend | [server_scripts.py](../backend/app/api/v1/server_scripts.py), [rule_engine.py](../backend/app/core/rule_engine.py) |
| Modell | [server_script.py](../backend/app/models/server_script.py) |
| Schemas | [server_script.py](../backend/app/schemas/server_script.py) |
| Reifegrad | **Funktional** |

Endpunkte: `/server-scripts/` CRUD + `POST /{id}/toggle`. Operator-/Field-Whitelists in `rule_engine.py`. **Lücken:** Whitelist klein, keine Trace-/Debug-Ansicht, nur Tasks anwendbar.

## 15. Client Scripts (Frontend-Regeln)

| Aspekt | Details |
|---|---|
| Backend | [client_scripts.py](../backend/app/api/v1/client_scripts.py) |
| Modell | [client_script.py](../backend/app/models/client_script.py) |
| Schemas | [client_script.py](../backend/app/schemas/client_script.py) |
| Frontend-Hook | [useClientScripts.ts](../frontend/src/hooks/useClientScripts.ts) |
| Service | [clientScript.service.ts](../frontend/src/services/clientScript.service.ts) |
| Reifegrad | **Funktional** |

Endpunkte: `GET /client-scripts/applicable?table_name=&sys_class_name=` (public), CRUD, `POST /{id}/toggle`. **Lücken:** Kein grafischer Editor; Interaktion mit Server-Scripts undokumentiert.

## 16. Benachrichtigungen

| Aspekt | Details |
|---|---|
| Modell | [notification.py](../backend/app/models/notification.py) |
| Backend-API | **Keine** |
| Frontend | Header-Badge in [DashboardLayout.tsx](../frontend/src/components/DashboardLayout.tsx) – ohne API-Anbindung |
| Reifegrad | **Stub** |

Modell mit `type`, `title`, `message`, `is_read`, `related_record_id` vorhanden, aber kein Router, keine Trigger, kein Versand.

## 17. Knowledge Base

| Aspekt | Details |
|---|---|
| Backend | **Keine** – kein Model, Endpoint oder Schema |
| Frontend | [PortalKnowledge.tsx](../frontend/src/pages/portal/PortalKnowledge.tsx) – hardgecodete Demo-Kacheln |
| Reifegrad | **Stub** |

## 18. Service-Katalog

| Aspekt | Details |
|---|---|
| Backend | **Keine Implementierung.** `task.service_id` existiert als optionale UUID ohne FK |
| Frontend | [PortalServices.tsx](../frontend/src/pages/portal/PortalServices.tsx) – hardgecodete Kacheln, Klick → "New Request" |
| Reifegrad | **Stub** |

## 19. UI-Shell – Tabs, Dark Mode, Global Search

| Aspekt | Details |
|---|---|
| Komponenten | [DashboardLayout.tsx](../frontend/src/components/DashboardLayout.tsx), [TabManager.tsx](../frontend/src/components/TabManager.tsx), [tabContentFactory.tsx](../frontend/src/components/tabContentFactory.tsx) |
| Context | [TabContext.tsx](../frontend/src/context/TabContext.tsx), [ThemeContext.tsx](../frontend/src/context/ThemeContext.tsx) |
| Reifegrad | **Funktional** |

Multi-Tab-System mit `localStorage`-Persistenz. Global Search erkennt Ticket-Nummern (INC/REQ/CHG/PRB/TSK/APR) und öffnet Form-Tab, sonst `/tasks/?search=...`. Dark Mode via Ant Design Algorithm-Toggle.

## 20. Globale Lücken-Übersicht

**Backend vorhanden, nicht eingebunden / kein UI:**
- `incidents.py`, `requests.py`, `models/incident.py`, `models/request.py` – **toter Code**
- `Notification`-Model – kein Router, keine Trigger
- `Role.permissions` – gepflegt, nicht enforced
- `mfa_enabled`, `failed_login_attempts`, `locked_until` – Felder ohne Logik
- `sla_target_respond`, `sla_target_resolve`, `sla_breach` – im Dashboard gelesen, nirgends gesetzt

**Frontend existiert, Backend Mock/fehlt:**
- PortalKnowledge (hardcoded)
- PortalServices (hardcoded)
- Notification-Badge (ohne API)
- `POST /auth/refresh` (Frontend ruft, Backend fehlt)

**Komplett fehlend:** SLA-Engine, Change-Workflows (CAB), Problem-Management (Known Errors), E-Mail-Inbound, Webhook-API, CMDB/CIs, Reporting/Export, Zeiterfassung, CSAT-Surveys.

**Größtes Risiko:** Das RBAC-Schema ist voll modelliert, aber alle Endpunkte prüfen nur `is_admin`/`is_support_agent`. Permission-Strings werden an keiner Stelle ausgewertet.
