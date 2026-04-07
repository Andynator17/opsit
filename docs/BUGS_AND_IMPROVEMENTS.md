# OpsIT — Bug- und Verbesserungs-Report (Stand 2026-04-07)

## Übersicht (sortiert nach Severity)

| # | Severity | Titel | Ort |
|---|---|---|---|
| 1 | [CRITICAL] | Privilege Escalation via `PATCH /users/me` (is_admin etc. über Body setzbar) | `backend/app/api/v1/users.py:26` |
| 2 | [CRITICAL] | JWT Refresh-Token als Access-Token einsetzbar (kein `type`-Check) | `backend/app/core/dependencies.py:16` |
| 3 | [CRITICAL] | Klartext-JWTs im Repo-Root + fehlendes `.gitignore` | Repo-Root (`temp_token.txt` u.a.) |
| 4 | [CRITICAL] | Öffentlicher `/auth/register` vergibt ersten Tenant+Company an jeden | `backend/app/api/v1/auth.py:63` |
| 5 | [CRITICAL] | Hardcodetes Default-Admin-Passwort `Admin123!` | `backend/app/core/config.py:36` |
| 6 | [CRITICAL] | Kein Secret-Rotation-Pfad (Single `SECRET_KEY`, keine `kid`) | `backend/app/core/config.py:21` |
| 7 | [HIGH] | `python-jose` 3.3.0 unmaintained, CVE-2024-33663/33664 | `backend/requirements.txt:13` |
| 8 | [HIGH] | RBAC-Helper vorhanden, aber **nirgends** verwendet — nur `is_admin`-Bool | `backend/app/core/permissions.py` (ungenutzt) |
| 9 | [HIGH] | `/auth/refresh`-Endpoint fehlt im Backend, Frontend ruft ihn auf | `backend/app/api/v1/auth.py`; `frontend/src/services/api.ts:101` |
| 10 | [HIGH] | Kein Logout/Token-Revocation | `backend/app/api/v1/auth.py` |
| 11 | [HIGH] | Keine Rate-Limits / kein Account-Lockout auf Login | `backend/app/api/v1/auth.py:20` |
| 12 | [HIGH] | `image/svg+xml` in Upload-Allowlist → Stored XSS | `backend/app/api/v1/attachments.py:38` |
| 13 | [HIGH] | Upload vertraut Client-`content_type` und Client-Dateiendung | `backend/app/api/v1/attachments.py:107,122` |
| 14 | [HIGH] | CORS mit Dev-Fallback + `allow_credentials=True`, kein Prod-Guard | `backend/app/main.py:22` |
| 15 | [HIGH] | Race Condition bei Ticketnummern-Generierung (COUNT+1) | `backend/app/api/v1/tasks.py:124` |
| 16 | [HIGH] | Portal-Slug global-unique statt tenant-scoped → Enumeration-Leak | `backend/app/api/v1/portals.py:31` |
| 17 | [HIGH] | Frontend hält Access- und Refresh-Token in `localStorage` | `frontend/src/services/api.ts:36` |
| 18 | [MEDIUM] | `get_db()` committet implizit am Request-Ende | `backend/app/core/database.py:30` |
| 19 | [MEDIUM] | Total-Count in `roles` via `len(all())` statt `func.count` | `backend/app/api/v1/roles.py:50` |
| 20 | [MEDIUM] | `@app.on_event` deprecated — Lifespan nutzen | `backend/app/main.py:95` |
| 21 | [MEDIUM] | `datetime.utcnow()` verwendet (naive, deprecated) | `backend/app/api/v1/auth.py:46` |
| 22 | [MEDIUM] | Passwort-Policy nur `min_length=8` | `backend/app/schemas/user.py:35` |
| 23 | [MEDIUM] | AuditLog-Total via `len(logs)` | `backend/app/api/v1/audit_logs.py:52` |
| 24 | [MEDIUM] | Task-Listen nicht company-scoped (Multi-Company-Leak im Tenant) | `backend/app/api/v1/tasks.py:195` |
| 25 | [MEDIUM] | Failed-Login-Counter wird nie inkrementiert | `backend/app/api/v1/auth.py:38` |
| 26 | [MEDIUM] | Attachment-Download ohne `nosniff`/CSP-Sandbox | `backend/app/api/v1/attachments.py:212` |
| 27 | [MEDIUM] | AuthContext-Init ohne Cancellation (Race bei StrictMode) | `frontend/src/context/AuthContext.tsx:22` |
| 28 | [MEDIUM] | StrictMode Double-Mount: doppelte `/me`-Fetches | `frontend/src/context/AuthContext.tsx:45` |
| 29 | [LOW] | 19 `any`-Nutzungen im Frontend | diverse |
| 30 | [LOW] | Keine Tests, kein CI, kein Dockerfile | Repo-Root |
| 31 | [LOW] | PowerShell-Wildwuchs (kill_*, restart_*, nuke_*) im Root | Repo-Root |
| 32 | [LOW] | `UserResponse` leakt `failed_login_attempts`/`locked_until` in Listen | `backend/app/schemas/user.py:62` |
| 33 | [LOW] | `CryptContext(deprecated="auto")` mit nur einem Schema wirkungslos | `backend/app/core/security.py:10` |

---

## Details

### 1. [CRITICAL] Privilege Escalation via `PATCH /users/me`
**Ort:** [users.py:26](../backend/app/api/v1/users.py#L26), [user.py:68](../backend/app/schemas/user.py#L68)
**Beschreibung:** `PATCH /users/me` nutzt
```python
update_data = user_update.model_dump(exclude_unset=True)
for field, value in update_data.items():
    setattr(current_user, field, value)
```
`UserUpdate` exponiert u.a. `is_admin`, `is_support_agent`, `is_active`, `is_vip`, `primary_company_id`, `user_type`. Jeder eingeloggte Nutzer kann sich per `PATCH /users/me {"is_admin": true}` zum Admin machen.
**Risiko:** Vollständige App-Übernahme, kombiniert mit #4 sogar aus dem Internet.
**Fix:** Separates `UserSelfUpdate`-Schema ohne Privilege-Felder, oder harte Whitelist:
```python
SELF_EDITABLE = {"first_name","last_name","phone","mobile","language","timezone","avatar_url"}
for f, v in user_update.model_dump(exclude_unset=True).items():
    if f in SELF_EDITABLE:
        setattr(current_user, f, v)
```

### 2. [CRITICAL] Refresh-Token ist als Access-Token nutzbar
**Ort:** [dependencies.py:16](../backend/app/core/dependencies.py#L16), [security.py:46](../backend/app/core/security.py#L46)
**Beschreibung:** `create_*_token` schreibt `type: access|refresh`, `get_current_user` prüft es aber nicht. Ein 7-Tage-Refresh-Token funktioniert damit als vollwertiger Access-Token.
**Fix:**
```python
payload = decode_token(token)
if payload is None or payload.get("type") != "access":
    raise credentials_exception
```
Analog später beim `/auth/refresh` zwingend `type == "refresh"`.

### 3. [CRITICAL] Klartext-Secrets im Repo-Root / kein `.gitignore`
**Ort:** Repo-Root: `temp_token.txt`, `login.json`, `token_response.json`, `login_test.json`.
**Verifiziert:** `temp_token.txt` enthält echten Admin-JWT inkl. `tenant_id` und `user_id`. Im gesamten Projekt fehlt `.gitignore`.
**Fix:**
1. Dateien löschen (`git rm --cached` wenn getrackt).
2. `.gitignore` mit `.env*`, `temp_token.txt`, `login*.json`, `token_*.json`, `uploads/`, `backend/.venv/`, `node_modules/`, `dist/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `openapi_check.json`.
3. `SECRET_KEY` rotieren, damit alle existierenden Tokens ungültig werden.

### 4. [CRITICAL] Öffentlicher `/auth/register` mit `select(Tenant).limit(1)`
**Ort:** [auth.py:63](../backend/app/api/v1/auth.py#L63)
**Beschreibung:** Endpoint ist nicht auth-geschützt, wählt den ersten `Tenant` und die erste `Company` der DB — jeder im Internet kann sich in den Produktiv-Tenant einschleusen. Kombiniert mit #1 = Admin-Takeover.
**Fix:** Endpoint deaktivieren oder an Invitation-Token / Tenant-spezifischen Flow binden.

### 5. [CRITICAL] Hardcodetes Default-Passwort
**Ort:** [config.py:35-36](../backend/app/core/config.py#L35-L36)
```python
FIRST_ADMIN_EMAIL: str = "admin@opsit.local"
FIRST_ADMIN_PASSWORD: str = "Admin123!"
```
**Fix:** Kein Default im Code — bei fehlender Env-Var hart abbrechen oder zufälliges Passwort erzeugen und Passwortwechsel bei Erst-Login erzwingen.

### 6. [CRITICAL] Kein Secret-Rotation-Pfad
**Ort:** [config.py:21](../backend/app/core/config.py#L21)
**Fix:** `SECRET_KEYS: list[str]` (primär = `[0]` zum Signieren, alle zum Verifizieren) + JWT-Header `kid`. Bei Rotation bleiben alte Sessions kurz gültig, bis sie auslaufen.

### 7. [HIGH] `python-jose` unmaintained + CVEs
**Ort:** [requirements.txt:13](../backend/requirements.txt#L13) (`python-jose[cryptography]==3.3.0`)
**Relevante CVEs:** CVE-2024-33663 (Algorithm Confusion), CVE-2024-33664 (JWT-Bomb DoS). Projekt seit Jahren ohne Release.
**Fix:** Migration auf `PyJWT>=2.8`:
```python
import jwt
encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```
`python-jose` entfernen.

### 8. [HIGH] RBAC ist totes Code-Gewicht
**Ort:** [permissions.py](../backend/app/core/permissions.py) (und die fehlenden Verwendungen in `backend/app/api/v1/*.py`)
**Beschreibung:** `permissions.py` definiert `get_user_permissions`, `check_permission` — eine Grep-Suche über `backend/app/api` findet **null** Nutzungen. Alle Endpoints kennen nur `get_current_user` / `get_current_admin_user` (reiner `is_admin`-Bool). Roles, Permission-Groups, Permissions existieren in der DB, beeinflussen aber nichts.
**Fix:** Factory `require_permission("incident.close")` als FastAPI-Dependency; in allen relevanten Routen einsetzen.

### 9. [HIGH] `/auth/refresh` fehlt
**Ort:** [auth.py](../backend/app/api/v1/auth.py), aufgerufen in [api.ts:101](../frontend/src/services/api.ts#L101)
**Beschreibung:** Frontend-Interceptor versucht `POST /auth/refresh` — Backend hat diese Route nicht registriert (in `main.py` ist nur `auth.router` eingebunden, `auth.py` definiert nur `/login`, `/register`, `/me`). Nach Ablauf der 15-Minuten-Session wird der Nutzer zwingend ausgeloggt.
**Fix:** Route implementieren (mit `type == "refresh"` Check, Rotation + Reuse-Detection).

### 10. [HIGH] Kein Logout / keine Revocation
**Fix:** `POST /auth/logout` mit DB/Redis-Blacklist; alternativ `token_version` pro User als Claim, Inkrement bei Logout/Passwortwechsel.

### 11. [HIGH] Keine Rate-Limits / kein Account-Lockout
**Ort:** [auth.py:20](../backend/app/api/v1/auth.py#L20)
**Beschreibung:** `failed_login_attempts` wird nur bei Erfolg auf 0 gesetzt, **nie inkrementiert**. Kein Lockout, kein IP-Rate-Limit. Brute-Force ist trivial.
**Fix:** Fehlerpfad hochzählen + `locked_until` setzen + `slowapi`-IP-Limit (5/min).

### 12. [HIGH] SVG-Upload erlaubt (Stored XSS)
**Ort:** [attachments.py:38](../backend/app/api/v1/attachments.py#L38)
**Beschreibung:** `image/svg+xml` in `ALLOWED_CONTENT_TYPES`. SVGs können `<script>` enthalten. `FileResponse` setzt `media_type=attachment.content_type`, sodass der Browser das SVG im App-Origin rendert → Cookie/Token-Diebstahl.
**Fix:** SVG streichen oder beim Download `Content-Disposition: attachment` + `Content-Security-Policy: sandbox` + `X-Content-Type-Options: nosniff`. Idealerweise separate File-Subdomain.

### 13. [HIGH] Client-`content_type`/Filename vertraut
**Ort:** [attachments.py:107](../backend/app/api/v1/attachments.py#L107), [attachments.py:122](../backend/app/api/v1/attachments.py#L122)
```python
if upload_file.content_type not in ALLOWED_CONTENT_TYPES: ...
file_ext = os.path.splitext(upload_file.filename or "file")[1]
stored_name = f"{uuid.uuid4()}{file_ext}"
```
**Beschreibung:** `content_type` kommt vom Client und kann gefaked werden. `file_ext` kommt aus dem Client-Filename und kann z.B. `.pdf\u202e.exe` sein.
**Fix:** MIME serverseitig per Magic-Bytes verifizieren (`python-magic`), `file_ext` aus dem verifizierten MIME ableiten (Whitelist-Mapping), niemals aus dem Client-Filename.

### 14. [HIGH] CORS-Fallback mit `allow_credentials`
**Ort:** [main.py:22-34](../backend/app/main.py#L22-L34)
**Fix:** In Prod harten Guard:
```python
if not settings.DEBUG and not settings.BACKEND_CORS_ORIGINS:
    raise RuntimeError("BACKEND_CORS_ORIGINS must be set in production")
if "*" in cors_origins:
    raise RuntimeError("Wildcard origins incompatible with allow_credentials=True")
```

### 15. [HIGH] Ticketnummern-Race
**Ort:** [tasks.py:124](../backend/app/api/v1/tasks.py#L124)
**Beschreibung:** `COUNT(*) + 1` unter parallelen Requests → doppelte Nummern. `is_deleted` nicht ausgeschlossen → nach Löschung Kollision mit historischen Nummern.
**Fix:** Eigene `ticket_sequences(tenant_id, sys_class_name, next_value)`-Tabelle mit `SELECT ... FOR UPDATE` / `UPDATE ... RETURNING`, oder PG-Sequence pro (tenant, class). `UNIQUE(tenant_id, number)` als Safety-Net.

### 16. [HIGH] Portal-Slug global-unique
**Ort:** [portals.py:31](../backend/app/api/v1/portals.py#L31)
**Beschreibung:** Uniqueness-Check ohne `tenant_id` — Tenant-Enumeration via 409.
**Fix:** `Portal.tenant_id == current_user.tenant_id` in den Check aufnehmen, DB-Constraint `UNIQUE(tenant_id, slug) WHERE is_deleted=false`.

### 17. [HIGH] Tokens in `localStorage`
**Ort:** [api.ts:36](../frontend/src/services/api.ts#L36)
**Fix (Stufenplan):** Access-Token in Memory (Interceptor-Closure), Refresh-Token kurzfristig in `sessionStorage`, mittelfristig Backend-Cookie `HttpOnly; Secure; SameSite=Strict`. CSP-Header serverseitig.

### 18. [MEDIUM] `get_db()` committet implizit
**Ort:** [database.py:30-38](../backend/app/core/database.py#L30-L38)
**Beschreibung:** `yield session; await session.commit()` committet jeden Endpoint-Read automatisch, auch wenn unbeabsichtigt Änderungen im Session-State stehen (z.B. `setattr` für Caching, `db.add` + früher Return).
**Fix:** Implicit-Commit entfernen, Endpoints committen explizit (machen sie bereits überall).

### 19. [MEDIUM] Ineffizienter Count in `roles.py`
**Ort:** [roles.py:50-58](../backend/app/api/v1/roles.py#L50-L58)
```python
count_result = await db.execute(select(Role).where(...))
total = len(count_result.scalars().all())
```
**Fix:** `select(func.count(Role.id)).where(...)`.

### 20. [MEDIUM] `@app.on_event` deprecated
**Ort:** [main.py:95](../backend/app/main.py#L95), [main.py:104](../backend/app/main.py#L104)
**Fix:** `asynccontextmanager` + `FastAPI(lifespan=lifespan)`.

### 21. [MEDIUM] `datetime.utcnow()`
**Ort:** [auth.py:46](../backend/app/api/v1/auth.py#L46) — naive, in Python 3.12+ deprecated. `security.py` nutzt bereits korrekt `datetime.now(timezone.utc)`.

### 22. [MEDIUM] Schwache Passwort-Policy
**Ort:** [user.py:35](../backend/app/schemas/user.py#L35) (`min_length=8`)
**Fix:** Custom Validator (>=12 Zeichen, >=3 von 4 Zeichenklassen), optional HIBP-Pwned-Password-Check.

### 23. [MEDIUM] AuditLog-Total per `len`
**Ort:** [audit_logs.py:49-52](../backend/app/api/v1/audit_logs.py#L49-L52). Analog zu #19. Fehlt zusätzlich Pagination.

### 24. [MEDIUM] Task-Listen nicht company-scoped
**Ort:** [tasks.py:195](../backend/app/api/v1/tasks.py#L195) — filtert nur per `tenant_id`. In Multi-Company-Mandanten sehen alle Nutzer alle Firmen-Tickets. Je nach Kundenmodell ein Informationsleak.
**Fix:** Default `Task.company_id == current_user.primary_company_id`; Support-Agents mit `multi_company`-Permission ausnehmen.

### 25. [MEDIUM] Failed-Login-Counter wird nie erhöht
Siehe #11 — `user.failed_login_attempts += 1` im Fehlerpfad + `locked_until` setzen.

### 26. [MEDIUM] Attachment-Download-Hardening
**Ort:** [attachments.py:212](../backend/app/api/v1/attachments.py#L212) — fehlt `X-Content-Type-Options: nosniff`, CSP, ggf. separater Origin.

### 27. [MEDIUM] AuthContext ohne Cancellation
**Ort:** [AuthContext.tsx:22-46](../frontend/src/context/AuthContext.tsx#L22-L46)
**Fix:** `let cancelled = false; return () => { cancelled = true; }`.

### 28. [MEDIUM] StrictMode Double-Effect
Siehe #27 — unter React 19 StrictMode läuft `initAuth` doppelt ohne Abort und feuert zwei `/me`-Fetches.

### 29. [LOW] `any` im Frontend
19 Treffer in 9 Dateien (`useClientScripts.ts`, `clientScript.service.ts`, `StatusWorkflow.tsx`, `portal/PortalNewTicket.tsx`, `portal/PortalTicketDetail.tsx` etc.). Ersetzen durch `unknown` + Narrowing oder konkrete Typen.

### 30. [LOW] Keine Tests, CI, Dockerfile
Nur Ad-hoc-Skripte `backend/test_tasks_api.py`, `check_dashboard_tasks.py`. Keine `tests/`-Suite, kein `.github/workflows/`, kein `Dockerfile`.

### 31. [LOW] PowerShell-Wildwuchs im Root
11 `.ps1`/`.bat`-Skripte zum Killen/Restarten des Backends weisen auf hängende Uvicorn-Workers hin. Root-Cause (wahrscheinlich Reload + hängende DB-Connections) sollte adressiert werden; Skripte in `scripts/` konsolidieren.

### 32. [LOW] `UserResponse` leakt Security-Metadaten
`failed_login_attempts`, `locked_until` sind in jedem `GET /users/`-Response sichtbar. Auf Admin-Schema beschränken.

### 33. [LOW] `CryptContext(deprecated="auto")` wirkungslos
**Ort:** [security.py:10](../backend/app/core/security.py#L10) — mit nur einem Schema nutzlos.

---

## Zusammenfassung

**33 Findings:** 6 Critical / 11 High / 11 Medium / 5 Low.

**Top-3-Risiken:**
1. **Privilege Escalation `PATCH /users/me`** (#1) — jeder Nutzer kann sich per Standardschema zum Admin machen.
2. **Klartext-Admin-JWT im Repo-Root** (#3) ohne `.gitignore` — sofortiger Totalverlust beim ersten `git push`.
3. **Refresh-Token als Access-Token** (#2) kombiniert mit **RBAC nur als `is_admin`-Bool** (#8) und **kein Login-Lockout** (#11) — extrem schwache Auth-Oberfläche.

**Quick-Wins (heute machbar):** Self-Update-Whitelist (#1), `type=="access"`-Check in `get_current_user` (#2), `.gitignore` + Secrets entfernen + Rotation (#3), SVG aus Upload-Allowlist (#12), `datetime.utcnow()` -> `datetime.now(timezone.utc)` (#21), Lifespan statt `on_event` (#20), `login`-Fehlerzähler + Lockout (#11/25), Portal-Slug tenant-scoped (#16).

**Mittelfristige Pflicht:** `/auth/refresh`-Endpoint + Logout/Revocation, `python-jose` -> `PyJWT`, RBAC-Enforcement in allen Endpoints, Ticketnummern-Sequence-Tabelle, Upload-Hardening (Magic-Sniffing), Frontend-Token-Storage auf HttpOnly-Cookie, Tests + CI + Dockerfile.
