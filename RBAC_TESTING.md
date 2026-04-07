# RBAC System Testing Guide

## Overview
This document provides testing instructions for the OpsIT RBAC (Role-Based Access Control) system.

## System Architecture

### Permission Groups
- **Purpose**: Define what users CAN DO
- **Contains**: Users + Roles
- **Example**: "Helpdesk Agent" permission group contains:
  - Roles: Incident Agent, Request Agent, Task Agent
  - Members: User A, User B, User C
- **Inheritance**: Users in a permission group inherit ALL roles from that group

### Support Groups
- **Purpose**: Define WHO GETS ASSIGNED tickets
- **Contains**: Users only (for ticket routing)
- **Example**: "Network Support Team", "Desktop Support Team"

### Roles
- **Format**: `{Module} {Level}` (e.g., "Incident Agent", "Request Admin")
- **4 Standard Levels per Module**:
  1. **Read**: View only
  2. **Read & Create**: View + Create
  3. **Agent**: View + Create + Update + Resolve
  4. **Admin**: Full control (including delete, manage settings)

### Modules
- Incident
- Request
- User
- Company
- Support Group
- Category
- Dashboard
- Role
- Permission Group

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

### 1. Roles Management

#### List All Roles
```bash
GET /roles
Query Parameters:
  - module (optional): Filter by module (incident, request, user, etc.)
  - level (optional): Filter by level (read, read_create, agent, admin)
  - skip (optional): Pagination offset
  - limit (optional): Number of results (default: 100)
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/roles" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "total": 30,
  "roles": [
    {
      "id": "uuid",
      "tenant_id": "uuid",
      "name": "Incident Agent",
      "code": "incident_agent",
      "description": "Can view, create, update, assign, and resolve incidents",
      "module": "incident",
      "level": "agent",
      "permissions": [
        "incident.read",
        "incident.create",
        "incident.update",
        "incident.assign",
        "incident.resolve"
      ],
      "is_system_role": true,
      "is_active": true,
      "created_at": "2026-02-10T12:41:01.168Z",
      "updated_at": "2026-02-10T12:41:01.168Z"
    }
  ]
}
```

#### Get Role by ID
```bash
GET /roles/{role_id}
```

#### Create Custom Role (Admin Only)
```bash
POST /roles
Content-Type: application/json

{
  "name": "Custom Role Name",
  "code": "custom_role_code",
  "description": "Role description",
  "module": "incident",
  "level": "custom",
  "permissions": ["incident.read", "incident.create"],
  "is_system_role": false
}
```

#### Update Role (Admin Only)
```bash
PATCH /roles/{role_id}
Content-Type: application/json

{
  "name": "Updated Role Name",
  "description": "Updated description",
  "permissions": ["incident.read", "incident.create", "incident.update"]
}
```

**Note**: System roles cannot be modified.

#### Delete Role (Admin Only)
```bash
DELETE /roles/{role_id}
```

**Note**: System roles cannot be deleted.

---

### 2. Permission Groups Management

#### List All Permission Groups
```bash
GET /permission-groups
Query Parameters:
  - skip (optional): Pagination offset
  - limit (optional): Number of results (default: 100)
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/permission-groups" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "total": 2,
  "permission_groups": [
    {
      "id": "uuid",
      "tenant_id": "uuid",
      "name": "Helpdesk Agent",
      "description": "Standard helpdesk agent with incident and request permissions",
      "members": [
        {
          "id": "uuid",
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        }
      ],
      "roles": [
        {
          "id": "uuid",
          "name": "Incident Agent",
          "code": "incident_agent",
          "module": "incident",
          "level": "agent"
        },
        {
          "id": "uuid",
          "name": "Request Agent",
          "code": "request_agent",
          "module": "request",
          "level": "agent"
        }
      ],
      "is_active": true,
      "created_at": "2026-02-10T12:00:00.000Z",
      "updated_at": "2026-02-10T12:00:00.000Z"
    }
  ]
}
```

#### Get Permission Group by ID
```bash
GET /permission-groups/{group_id}
```

#### Create Permission Group (Admin Only)
```bash
POST /permission-groups
Content-Type: application/json

{
  "name": "Helpdesk Agent",
  "description": "Standard helpdesk agent with incident and request permissions"
}
```

#### Update Permission Group (Admin Only)
```bash
PATCH /permission-groups/{group_id}
Content-Type: application/json

{
  "name": "Updated Group Name",
  "description": "Updated description"
}
```

#### Delete Permission Group (Admin Only)
```bash
DELETE /permission-groups/{group_id}
```

---

### 3. Permission Group Members Management

#### Add Members to Permission Group (Admin Only)
```bash
POST /permission-groups/{group_id}/members
Content-Type: application/json

{
  "user_ids": ["user_uuid_1", "user_uuid_2"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Helpdesk Agent",
  "members": [...],
  "roles": [...]
}
```

#### Remove Member from Permission Group (Admin Only)
```bash
DELETE /permission-groups/{group_id}/members/{user_id}
```

---

### 4. Permission Group Roles Management

#### Add Roles to Permission Group (Admin Only)
```bash
POST /permission-groups/{group_id}/roles
Content-Type: application/json

{
  "role_ids": ["role_uuid_1", "role_uuid_2"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Helpdesk Agent",
  "members": [...],
  "roles": [...]
}
```

#### Remove Role from Permission Group (Admin Only)
```bash
DELETE /permission-groups/{group_id}/roles/{role_id}
```

---

## Testing Workflow

### 1. Get Authentication Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@opsit.demo",
    "password": "your_password"
  }'
```

Save the `access_token` from the response.

### 2. List Available Roles
```bash
curl -X GET "http://localhost:8000/api/v1/roles" \
  -H "Authorization: Bearer <token>"
```

### 3. Filter Roles by Module
```bash
curl -X GET "http://localhost:8000/api/v1/roles?module=incident" \
  -H "Authorization: Bearer <token>"
```

### 4. Create a Permission Group
```bash
curl -X POST "http://localhost:8000/api/v1/permission-groups" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Helpdesk Agent",
    "description": "Standard helpdesk agent with incident and request permissions"
  }'
```

Save the permission group `id` from the response.

### 5. Add Roles to Permission Group
First, get the role IDs for "Incident Agent" and "Request Agent":
```bash
curl -X GET "http://localhost:8000/api/v1/roles?module=incident&level=agent" \
  -H "Authorization: Bearer <token>"
```

Then add the roles:
```bash
curl -X POST "http://localhost:8000/api/v1/permission-groups/<group_id>/roles" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_ids": ["<incident_agent_role_id>", "<request_agent_role_id>"]
  }'
```

### 6. Add Members to Permission Group
```bash
curl -X POST "http://localhost:8000/api/v1/permission-groups/<group_id>/members" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": ["<user_id_1>", "<user_id_2>"]
  }'
```

### 7. Verify Permission Group
```bash
curl -X GET "http://localhost:8000/api/v1/permission-groups/<group_id>" \
  -H "Authorization: Bearer <token>"
```

## Permission Checking

The system includes permission checking utilities that can be used in API endpoints:

```python
from app.core.permissions import require_permission, require_permissions, require_any_permission

# Single permission
@router.get("/incidents")
async def get_incidents(user: User = Depends(require_permission("incident.read"))):
    ...

# Multiple permissions (ALL required)
@router.post("/incidents")
async def create_incident(
    user: User = Depends(require_permissions("incident.create", "incident.read"))
):
    ...

# Any permission (at least ONE required)
@router.get("/tickets")
async def get_tickets(
    user: User = Depends(require_any_permission("incident.read", "request.read"))
):
    ...
```

## Default Roles

The system comes with 30 pre-seeded roles:

### Incident Module
- Incident Read
- Incident Read & Create
- Incident Agent
- Incident Admin

### Request Module
- Request Read
- Request Read & Create
- Request Agent
- Request Admin

### User Module
- User Read
- User Read & Create
- User Agent
- User Admin

### Company Module
- Company Read
- Company Read & Create
- Company Agent
- Company Admin

### Support Group Module
- Support Group Read
- Support Group Read & Create
- Support Group Agent
- Support Group Admin

### Category Module
- Category Read
- Category Read & Create
- Category Agent
- Category Admin

### Dashboard Module
- Dashboard View
- Dashboard Admin

### Role Module
- Role Read
- Role Admin

### Permission Group Module
- Permission Group Read
- Permission Group Admin

## Notes

1. **System Roles**: Cannot be modified or deleted (is_system_role = true)
2. **Admin Users**: Have wildcard permission "*" and bypass all permission checks
3. **Permission Inheritance**: Users inherit all permissions from all roles in all their permission groups
4. **Soft Deletes**: Deleted roles and permission groups are marked as is_deleted = true, not physically removed
5. **Multi-tenancy**: All data is isolated by tenant_id

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
