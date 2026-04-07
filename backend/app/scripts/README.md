# OpsIT Scripts

Scripts for database seeding and maintenance.

## RBAC Seed Script

Seeds the database with default roles and permission groups.

### Prerequisites

1. RBAC migration must be applied:
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

2. At least one tenant must exist in the database

### Usage

```bash
cd backend
python -m app.scripts.seed_rbac
```

### What it creates

#### Roles (13 total):

**Incident Management:**
- Incident Reader - Can view incidents
- Incident Agent - Can manage assigned incidents
- Incident Admin - Full control over incidents

**Request Management:**
- Request Reader - Can view requests
- Request Agent - Can manage assigned requests
- Request Admin - Full control over requests

**User Management:**
- User Reader - Can view users
- User Admin - Full control over users

**Company Management:**
- Company Reader - Can view companies
- Company Admin - Full control over companies

**Knowledge Base:**
- Knowledge Reader - Can view knowledge articles
- Knowledge Author - Can create and edit knowledge articles

**System:**
- System Administrator - Full system administration rights

#### Permission Groups (6 total):

1. **System Administrators** - Full system access
   - Roles: system_admin

2. **Helpdesk Agents** - Standard helpdesk agents
   - Roles: incident_agent, request_agent, knowledge_read, user_read, company_read

3. **Helpdesk Managers** - Helpdesk team leads
   - Roles: incident_admin, request_admin, knowledge_author, user_read, company_read

4. **End Users** - Standard end users
   - Roles: incident_read, request_read, knowledge_read

5. **Knowledge Authors** - Can create KB articles
   - Roles: knowledge_author, incident_read, request_read

6. **User Administrators** - Can manage users and companies
   - Roles: user_admin, company_admin, incident_read, request_read

### Re-running the script

The script is idempotent - it will skip existing roles and permission groups, so it's safe to run multiple times.

### Next Steps

After running the seed script:

1. Go to the frontend: `/permission-groups`
2. Edit the permission groups to add users
3. Or go to user management and add users to permission groups via the "Permission Groups" tab
