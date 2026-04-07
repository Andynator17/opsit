# Support Groups API - Complete Reference

## Overview
Support Groups define **WHO GETS ASSIGNED** tickets. They are separate from Permission Groups and are used for ticket routing and assignment.

## Difference: Permission Groups vs Support Groups

### Permission Groups
- **Purpose**: Define what users CAN DO
- **Contains**: Users + Roles
- **Example**: "Helpdesk Agent" permission group
  - Roles: Incident Agent, Request Agent
  - Members: User A, User B
  - Result: Both users can manage incidents and requests

### Support Groups
- **Purpose**: Define WHO GETS ASSIGNED tickets
- **Contains**: Users only (for ticket routing)
- **Example**: "Network Support Team", "Desktop Support Team"
- **Features**:
  - Team leads (users with elevated responsibility)
  - Assignment methods (manual, round-robin, load-balanced)
  - Group email and manager

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### 1. Create Support Group (Admin Only)
```bash
POST /support-groups
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Network Support Team",
  "description": "Handles network and infrastructure issues",
  "email": "network@company.com",
  "group_type": "support",
  "assignment_method": "round_robin",
  "manager_id": "manager_user_uuid",
  "member_ids": ["user_uuid_1", "user_uuid_2"]
}
```

**Fields:**
- `name` (required): Group display name
- `description` (optional): Group description
- `email` (optional): Group email address
- `group_type` (default: "support"): Type of group (support, operations, development, management)
- `assignment_method` (default: "manual"): How tickets are assigned (manual, round_robin, load_balanced, skill_based)
- `manager_id` (optional): UUID of the group manager
- `member_ids` (optional): List of user UUIDs to add as members

**Response:**
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "Network Support Team",
  "description": "Handles network and infrastructure issues",
  "email": "network@company.com",
  "group_type": "support",
  "assignment_method": "round_robin",
  "manager_id": "uuid",
  "is_active": true,
  "created_at": "2026-02-10T12:00:00Z",
  "updated_at": "2026-02-10T12:00:00Z",
  "manager": {
    "id": "uuid",
    "email": "manager@company.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "members": [
    {
      "id": "uuid",
      "email": "user1@company.com",
      "first_name": "Jane",
      "last_name": "Smith"
    }
  ]
}
```

---

### 2. List All Support Groups
```bash
GET /support-groups
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total": 5,
  "groups": [
    {
      "id": "uuid",
      "name": "Network Support Team",
      "description": "Handles network issues",
      ...
    }
  ]
}
```

---

### 3. Get Support Group by ID
```bash
GET /support-groups/{group_id}
Authorization: Bearer <token>
```

**Response:** Same as Create response

---

### 4. Update Support Group (Admin Only)
```bash
PATCH /support-groups/{group_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Updated Network Team",
  "description": "Updated description",
  "assignment_method": "load_balanced"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

---

### 5. Add Members to Support Group (Admin Only)
```bash
POST /support-groups/{group_id}/members
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_ids": ["user_uuid_1", "user_uuid_2", "user_uuid_3"]
}
```

**Features:**
- Adds multiple users at once
- Automatically sets `is_team_lead = false` for new members
- Skips users that are already members (no duplicates)

**Response:** Returns the updated support group with all members

---

### 6. Update Member Details (Admin Only) - NEW!
```bash
PATCH /support-groups/{group_id}/members/{user_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "is_team_lead": true
}
```

**Purpose:** Set or remove team lead status for a member

**Use Cases:**
- Promote a member to team lead: `{"is_team_lead": true}`
- Demote a team lead to regular member: `{"is_team_lead": false}`

**Response:** Returns the updated support group

---

### 7. Remove Member from Support Group (Admin Only)
```bash
DELETE /support-groups/{group_id}/members/{user_id}
Authorization: Bearer <token>
```

**Response:** 204 No Content

---

### 8. Delete Support Group (Admin Only)
```bash
DELETE /support-groups/{group_id}
Authorization: Bearer <token>
```

**Note:** This is a soft delete (sets `is_deleted = true`)

**Response:** 204 No Content

---

## Typical Workflows

### Workflow 1: Create a New Support Team
```bash
# 1. Create the group
POST /support-groups
{
  "name": "Desktop Support L1",
  "description": "First-line desktop support team",
  "email": "desktop-l1@company.com",
  "assignment_method": "round_robin"
}

# Save the group_id from response

# 2. Add team members
POST /support-groups/{group_id}/members
{
  "user_ids": ["user1_uuid", "user2_uuid", "user3_uuid"]
}

# 3. Set team lead
PATCH /support-groups/{group_id}/members/{user1_uuid}
{
  "is_team_lead": true
}
```

### Workflow 2: Reorganize Team
```bash
# 1. Remove old team lead status
PATCH /support-groups/{group_id}/members/{old_lead_uuid}
{
  "is_team_lead": false
}

# 2. Set new team lead
PATCH /support-groups/{group_id}/members/{new_lead_uuid}
{
  "is_team_lead": true
}

# 3. Add new members
POST /support-groups/{group_id}/members
{
  "user_ids": ["new_user1_uuid", "new_user2_uuid"]
}

# 4. Remove inactive members
DELETE /support-groups/{group_id}/members/{inactive_user_uuid}
```

---

## Group Types

- **support**: General support team (default)
- **operations**: Operations team
- **development**: Development team
- **management**: Management team

---

## Assignment Methods

- **manual**: Tickets are manually assigned by agents or managers
- **round_robin**: Tickets are automatically assigned in rotation
- **load_balanced**: Tickets are assigned based on current workload
- **skill_based**: Tickets are assigned based on agent skills (future feature)

---

## Team Lead Features

Team leads are regular members with the `is_team_lead` flag set to `true`.

**Current Behavior:**
- Team leads are marked in the database
- Can be used for UI display (show team lead badge)
- Can be used for approval workflows

**Future Enhancements:**
- Team leads can approve/reassign tickets within their group
- Team leads get notifications for escalated tickets
- Team leads can view team performance metrics

---

## Integration with Tickets

When creating or updating incidents/requests:

1. Set `assigned_group_id` to route to a support group
2. Optionally set `assigned_to` to assign to a specific user within that group
3. The group's `assignment_method` determines automatic assignment behavior

**Example:**
```json
{
  "title": "Network connectivity issue",
  "assigned_group_id": "network_team_uuid",
  "assigned_to": null  // Will be auto-assigned based on assignment_method
}
```

---

## Permissions

All support group management operations require **admin** privileges:
- Create group: Admin only
- Update group: Admin only
- Add/remove members: Admin only
- Update member details: Admin only
- Delete group: Admin only

Reading support groups is available to all authenticated users.

---

## Database Schema

### `support_groups` table
- `id` (UUID): Primary key
- `tenant_id` (UUID): Multi-tenancy
- `name` (string): Group name
- `description` (text): Description
- `email` (string): Group email
- `group_type` (string): Type of group
- `assignment_method` (string): Assignment strategy
- `manager_id` (UUID): FK to users
- `is_active` (boolean): Active flag
- `is_deleted` (boolean): Soft delete flag
- `created_at`, `updated_at` (timestamp)

### `group_members` association table
- `group_id` (UUID): FK to support_groups - **Primary Key**
- `user_id` (UUID): FK to users - **Primary Key**
- `is_team_lead` (boolean): Team lead flag

**Note:** The composite primary key (`group_id`, `user_id`) ensures no duplicate memberships.

---

## What's New in This Update

✅ **Added Schema:**
- `SupportGroupMemberUpdate`: For updating member details
- `MemberSummary`: Extended UserSummary with `is_team_lead` flag

✅ **Added Endpoint:**
- `PATCH /support-groups/{group_id}/members/{user_id}`: Update member details (set team lead)

✅ **Fixed:**
- PostgreSQL compatibility in add members endpoint (changed from SQLite's `OR IGNORE` to PostgreSQL's `ON CONFLICT DO NOTHING`)
- Proper handling of `is_team_lead` flag when adding members

✅ **Improved:**
- Better error messages
- Consistent admin-only checks
- Proper database session handling

---

## API Documentation

Full interactive API documentation available at:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

Look for the **support-groups** tag in the documentation.
