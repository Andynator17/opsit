# OpsIT - API Design

## API Architecture

### Design Principles
1. **RESTful** - Standard HTTP methods and status codes
2. **Versioned** - `/api/v1/` prefix
3. **JSON** - All requests and responses use JSON
4. **Stateless** - JWT tokens for authentication
5. **Hypermedia** - Links to related resources (HATEOAS light)
6. **Filtering & Pagination** - Standard query parameters
7. **Consistent** - Predictable patterns across endpoints
8. **Well-documented** - OpenAPI 3.0 (Swagger)

### Base URL
```
Production: https://api.opsit.eu
Tenant-specific: https://{tenant}.opsit.eu/api/v1
Development: http://localhost:8000/api/v1
```

### Authentication
```
Authorization: Bearer {jwt_token}
```

### Standard Headers
```
Request:
  Content-Type: application/json
  Authorization: Bearer {token}
  X-Tenant-ID: {tenant_uuid} (for multi-tenant)
  Accept-Language: en-US (for i18n)

Response:
  Content-Type: application/json
  X-Request-ID: {uuid} (for tracing)
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 999
  X-RateLimit-Reset: 1640000000
```

---

## Common Patterns

### Pagination
```
Query Parameters:
  ?page=1&page_size=50&sort=-created_at

Response:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 1000,
    "total_pages": 20,
    "has_next": true,
    "has_prev": false
  }
}

Default: page=1, page_size=50
Maximum page_size: 100
```

### Filtering
```
?status=open&priority=high&assigned_to=user-uuid
?created_at_gte=2024-01-01&created_at_lte=2024-12-31
?search=network+issue (full-text search)
?category_id=cat-uuid
```

### Sorting
```
?sort=created_at (ascending)
?sort=-created_at (descending, prefix with -)
?sort=-priority,created_at (multiple fields)
```

### Field Selection (Sparse Fieldsets)
```
?fields=id,title,status,priority (return only specified fields)
```

### Expansion (Include Related)
```
?include=assigned_to,reported_by,related_ci
```

### HTTP Status Codes
```
200 OK - Success
201 Created - Resource created
204 No Content - Success with no body (DELETE)
400 Bad Request - Validation error
401 Unauthorized - Authentication failed
403 Forbidden - Authorization failed
404 Not Found - Resource not found
409 Conflict - Resource conflict (duplicate)
422 Unprocessable Entity - Business logic error
429 Too Many Requests - Rate limit exceeded
500 Internal Server Error - Server error
503 Service Unavailable - Maintenance mode
```

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req-uuid",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

## API Endpoints

### Authentication & Users

#### POST /api/v1/auth/login
Login user
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "mfa_code": "123456" (optional, if MFA enabled)
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "agent",
    "tenant_id": "tenant-uuid"
  }
}
```

#### POST /api/v1/auth/refresh
Refresh access token
```json
Request:
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh..."
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "expires_in": 900
}
```

#### POST /api/v1/auth/logout
Logout (invalidate tokens)

#### POST /api/v1/auth/forgot-password
Request password reset
```json
Request:
{
  "email": "user@example.com"
}

Response: 200 OK
{
  "message": "Password reset email sent"
}
```

#### POST /api/v1/auth/reset-password
Reset password with token

#### POST /api/v1/auth/mfa/enable
Enable MFA

#### POST /api/v1/auth/mfa/verify
Verify MFA code

#### GET /api/v1/users/me
Get current user profile

#### PATCH /api/v1/users/me
Update current user profile

#### GET /api/v1/users
List users (admin only)

#### POST /api/v1/users
Create user (admin only)

#### GET /api/v1/users/{user_id}
Get user details

#### PATCH /api/v1/users/{user_id}
Update user

#### DELETE /api/v1/users/{user_id}
Deactivate user (soft delete)

---

### Incidents

#### GET /api/v1/incidents
List incidents
```
Query params:
  ?status=open,in_progress
  ?priority=high,critical
  ?assigned_to=user-uuid
  ?reported_by=user-uuid
  ?category_id=cat-uuid
  ?created_at_gte=2024-01-01
  ?search=network+down
  ?include=assigned_to,reported_by,related_ci
  ?page=1&page_size=50&sort=-created_at

Response: 200 OK
{
  "data": [
    {
      "id": "inc-uuid",
      "ticket_number": "INC0001234",
      "title": "Network connectivity issue",
      "description": "Users cannot access...",
      "status": "in_progress",
      "priority": "high",
      "urgency": "high",
      "impact": "medium",
      "category": {
        "id": "cat-uuid",
        "name": "Network"
      },
      "assigned_to": {
        "id": "user-uuid",
        "full_name": "Jane Smith"
      },
      "reported_by": {
        "id": "user-uuid",
        "full_name": "John Doe"
      },
      "reported_date": "2024-01-15T10:00:00Z",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "sla_due_date": "2024-01-15T14:00:00Z",
      "sla_breached": false
    }
  ],
  "pagination": {...}
}
```

#### POST /api/v1/incidents
Create incident
```json
Request:
{
  "title": "Network connectivity issue",
  "description": "Users in Building A cannot access...",
  "priority": "high", (optional, auto-calculated if not provided)
  "urgency": "high",
  "impact": "medium",
  "category_id": "cat-uuid",
  "subcategory_id": "subcat-uuid" (optional),
  "related_ci_id": "ci-uuid" (optional),
  "related_service_id": "svc-uuid" (optional),
  "reported_by_id": "user-uuid" (optional, defaults to current user),
  "custom_fields": {
    "affected_location": "Building A"
  }
}

Response: 201 Created
{
  "id": "inc-uuid",
  "ticket_number": "INC0001235",
  ...
}
```

#### GET /api/v1/incidents/{incident_id}
Get incident details

#### PATCH /api/v1/incidents/{incident_id}
Update incident
```json
Request:
{
  "status": "in_progress",
  "assigned_to_id": "user-uuid",
  "priority": "critical"
}

Response: 200 OK
```

#### DELETE /api/v1/incidents/{incident_id}
Delete incident (soft delete, admin only)

#### POST /api/v1/incidents/{incident_id}/assign
Assign incident
```json
Request:
{
  "assigned_to_id": "user-uuid" (optional),
  "assigned_group_id": "group-uuid" (optional)
}
```

#### POST /api/v1/incidents/{incident_id}/resolve
Resolve incident
```json
Request:
{
  "resolution": "Issue resolved by...",
  "resolution_category": "Fixed",
  "root_cause": "Network switch failure" (optional)
}
```

#### POST /api/v1/incidents/{incident_id}/close
Close incident
```json
Request:
{
  "close_notes": "User confirmed resolution"
}
```

#### POST /api/v1/incidents/{incident_id}/reopen
Reopen incident

---

### Requests (Service Requests)

#### GET /api/v1/requests
List requests

#### POST /api/v1/requests
Create request
```json
Request:
{
  "catalog_item_id": "item-uuid",
  "title": "Request for new laptop",
  "description": "Need new laptop for new employee",
  "urgency": "medium",
  "custom_fields": {
    "laptop_model": "ThinkPad X1",
    "delivery_location": "Building B"
  }
}

Response: 201 Created
```

#### GET /api/v1/requests/{request_id}
Get request details

#### PATCH /api/v1/requests/{request_id}
Update request

#### POST /api/v1/requests/{request_id}/approve
Approve request (approver only)
```json
Request:
{
  "comments": "Approved as per policy"
}
```

#### POST /api/v1/requests/{request_id}/reject
Reject request
```json
Request:
{
  "rejection_reason": "Insufficient budget"
}
```

#### POST /api/v1/requests/{request_id}/fulfill
Mark as fulfilled

---

### Comments (Work Notes)

#### GET /api/v1/incidents/{incident_id}/comments
List comments for incident

#### POST /api/v1/incidents/{incident_id}/comments
Add comment
```json
Request:
{
  "content": "Investigating the issue...",
  "comment_type": "work_note", (work_note, customer_note, resolution_note)
  "is_internal": false (visible to customer)
}

Response: 201 Created
```

#### PATCH /api/v1/comments/{comment_id}
Edit comment

#### DELETE /api/v1/comments/{comment_id}
Delete comment

---

### Attachments

#### POST /api/v1/incidents/{incident_id}/attachments
Upload attachment
```
Content-Type: multipart/form-data

Form data:
  file: <binary>
  is_public: true/false

Response: 201 Created
{
  "id": "att-uuid",
  "filename": "screenshot.png",
  "file_size": 102400,
  "mime_type": "image/png",
  "url": "https://storage.opsit.eu/attachments/..."
}
```

#### GET /api/v1/attachments/{attachment_id}
Download attachment

#### DELETE /api/v1/attachments/{attachment_id}
Delete attachment

---

### Service Catalog

#### GET /api/v1/catalog/items
List catalog items
```
Query params:
  ?category_id=cat-uuid
  ?is_active=true
  ?search=laptop

Response: 200 OK
{
  "data": [
    {
      "id": "item-uuid",
      "name": "New Laptop Request",
      "short_description": "Request a new laptop",
      "description": "Full description...",
      "category": {...},
      "icon": "laptop",
      "price": 0,
      "estimated_delivery": "2-3 business days",
      "approval_required": true,
      "form_schema": {
        "fields": [
          {
            "name": "laptop_model",
            "type": "select",
            "label": "Laptop Model",
            "required": true,
            "options": ["ThinkPad X1", "MacBook Pro"]
          }
        ]
      }
    }
  ]
}
```

#### GET /api/v1/catalog/items/{item_id}
Get catalog item details

#### POST /api/v1/catalog/items
Create catalog item (admin)

#### PATCH /api/v1/catalog/items/{item_id}
Update catalog item

---

### Configuration Items (CMDB)

#### GET /api/v1/cmdb/cis
List configuration items
```
Query params:
  ?ci_type_id=type-uuid
  ?status=active
  ?owner_id=user-uuid
  ?location_id=loc-uuid
  ?search=server

Response: 200 OK
```

#### POST /api/v1/cmdb/cis
Create CI

#### GET /api/v1/cmdb/cis/{ci_id}
Get CI details

#### PATCH /api/v1/cmdb/cis/{ci_id}
Update CI

#### DELETE /api/v1/cmdb/cis/{ci_id}
Delete CI

#### GET /api/v1/cmdb/cis/{ci_id}/relationships
Get CI relationships
```
Response: 200 OK
{
  "upstream": [
    {
      "ci": {...},
      "relationship_type": "depends_on"
    }
  ],
  "downstream": [
    {
      "ci": {...},
      "relationship_type": "supports"
    }
  ]
}
```

#### POST /api/v1/cmdb/cis/{ci_id}/relationships
Create CI relationship
```json
Request:
{
  "to_ci_id": "ci-uuid",
  "relationship_type_id": "rel-type-uuid"
}
```

#### GET /api/v1/cmdb/cis/{ci_id}/impact
Get impact analysis (affected services/CIs)

---

### Services

#### GET /api/v1/services
List services

#### POST /api/v1/services
Create service

#### GET /api/v1/services/{service_id}
Get service details

#### PATCH /api/v1/services/{service_id}
Update service

#### GET /api/v1/services/{service_id}/incidents
List incidents for service

---

### Categories

#### GET /api/v1/categories
List categories
```
Query params:
  ?category_type=incident,request,ci
  ?parent_id=parent-uuid (get subcategories)

Response: 200 OK (hierarchical)
```

#### POST /api/v1/categories
Create category (admin)

---

### Groups & Teams

#### GET /api/v1/groups
List groups

#### POST /api/v1/groups
Create group

#### GET /api/v1/groups/{group_id}
Get group details

#### GET /api/v1/groups/{group_id}/members
List group members

#### POST /api/v1/groups/{group_id}/members
Add member to group

#### DELETE /api/v1/groups/{group_id}/members/{user_id}
Remove member from group

---

### SLAs

#### GET /api/v1/slas
List SLAs

#### POST /api/v1/slas
Create SLA (admin)

#### GET /api/v1/slas/{sla_id}
Get SLA details

#### PATCH /api/v1/slas/{sla_id}
Update SLA

---

### Knowledge Base

#### GET /api/v1/knowledge/articles
List knowledge articles
```
Query params:
  ?status=published
  ?category_id=cat-uuid
  ?search=password+reset
  ?is_public=true

Response: 200 OK
```

#### POST /api/v1/knowledge/articles
Create article

#### GET /api/v1/knowledge/articles/{article_id}
Get article details

#### PATCH /api/v1/knowledge/articles/{article_id}
Update article

#### POST /api/v1/knowledge/articles/{article_id}/publish
Publish article

#### POST /api/v1/knowledge/articles/{article_id}/vote
Vote on article (helpful/not helpful)
```json
Request:
{
  "vote": "helpful" // or "not_helpful"
}
```

#### GET /api/v1/knowledge/articles/{article_id}/related
Get related articles

---

### Dashboards & Analytics

#### GET /api/v1/dashboard/summary
Get dashboard summary
```
Response: 200 OK
{
  "incidents": {
    "total": 150,
    "open": 45,
    "in_progress": 30,
    "pending": 10,
    "resolved_today": 5
  },
  "requests": {
    "total": 80,
    "pending_approval": 12,
    "in_fulfillment": 25
  },
  "sla_compliance": {
    "percentage": 95.5,
    "breached_today": 3
  },
  "my_tickets": {
    "assigned_to_me": 8,
    "reported_by_me": 3
  }
}
```

#### GET /api/v1/reports/incidents
Incident report
```
Query params:
  ?date_from=2024-01-01
  ?date_to=2024-01-31
  ?group_by=category,priority
  ?format=json,csv,pdf

Response: 200 OK
{
  "summary": {
    "total": 500,
    "resolved": 450,
    "mttr_hours": 4.5,
    "sla_compliance": 96.5
  },
  "by_category": [
    {
      "category": "Network",
      "count": 150,
      "percentage": 30
    }
  ]
}
```

#### GET /api/v1/reports/sla
SLA compliance report

#### GET /api/v1/reports/agent-performance
Agent performance report

---

### Workflows

#### GET /api/v1/workflows
List workflow definitions

#### POST /api/v1/workflows
Create workflow (admin)

#### GET /api/v1/workflows/{workflow_id}
Get workflow details

#### GET /api/v1/workflows/instances
List workflow instances (active workflows)

---

### Notifications

#### GET /api/v1/notifications
List notifications for current user
```
Response: 200 OK
{
  "data": [
    {
      "id": "notif-uuid",
      "title": "Incident INC0001234 assigned to you",
      "message": "High priority incident...",
      "notification_type": "assignment",
      "entity_id": "inc-uuid",
      "entity_type": "incident",
      "is_read": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "unread_count": 5
}
```

#### PATCH /api/v1/notifications/{notification_id}/read
Mark notification as read

#### POST /api/v1/notifications/read-all
Mark all as read

---

### Audit Logs

#### GET /api/v1/audit-logs
List audit logs (admin only)
```
Query params:
  ?user_id=user-uuid
  ?entity_type=incident
  ?entity_id=inc-uuid
  ?action=UPDATE
  ?date_from=2024-01-01
  ?date_to=2024-01-31

Response: 200 OK
{
  "data": [
    {
      "id": "log-uuid",
      "user": {
        "id": "user-uuid",
        "full_name": "John Doe"
      },
      "action": "UPDATE",
      "entity_type": "incident",
      "entity_id": "inc-uuid",
      "old_values": {"status": "new"},
      "new_values": {"status": "in_progress"},
      "timestamp": "2024-01-15T10:00:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

---

### Admin & Configuration

#### GET /api/v1/admin/settings
Get tenant settings (admin)

#### PATCH /api/v1/admin/settings
Update tenant settings

#### GET /api/v1/admin/stats
System statistics (admin)

#### POST /api/v1/admin/users/{user_id}/reset-password
Admin reset user password

#### POST /api/v1/admin/maintenance-mode
Enable/disable maintenance mode

---

### WebSocket API

#### Connection
```
wss://api.opsit.eu/ws?token={jwt_token}
```

#### Events (Server → Client)
```json
// Ticket assigned
{
  "event": "ticket.assigned",
  "data": {
    "ticket_id": "inc-uuid",
    "ticket_number": "INC0001234",
    "assigned_to_id": "user-uuid"
  }
}

// Ticket updated
{
  "event": "ticket.updated",
  "data": {
    "ticket_id": "inc-uuid",
    "changed_fields": ["status", "priority"]
  }
}

// New comment
{
  "event": "comment.created",
  "data": {
    "ticket_id": "inc-uuid",
    "comment_id": "comment-uuid"
  }
}

// Notification
{
  "event": "notification",
  "data": {
    "notification_id": "notif-uuid",
    "title": "New ticket assigned"
  }
}
```

#### Client → Server
```json
// Subscribe to ticket updates
{
  "action": "subscribe",
  "channel": "ticket.INC0001234"
}

// Typing indicator
{
  "action": "typing",
  "ticket_id": "inc-uuid"
}
```

---

## Webhooks (Outgoing)

Customers can register webhooks for events:

#### POST /api/v1/webhooks
Register webhook
```json
Request:
{
  "url": "https://customer.com/webhook",
  "events": ["incident.created", "incident.resolved"],
  "secret": "webhook-secret" (for signature verification)
}
```

#### Webhook Payload
```json
{
  "event": "incident.created",
  "timestamp": "2024-01-15T10:00:00Z",
  "data": {
    "id": "inc-uuid",
    "ticket_number": "INC0001234",
    ...
  },
  "signature": "sha256=..." (HMAC)
}
```

---

## Rate Limiting

```
Tier 1 (End User):
  - 100 requests/minute
  - 1000 requests/hour

Tier 2 (Agent):
  - 300 requests/minute
  - 3000 requests/hour

Tier 3 (Admin/API):
  - 1000 requests/minute
  - 10000 requests/hour

Response when exceeded:
  HTTP 429 Too Many Requests
  {
    "error": {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "Rate limit exceeded",
      "retry_after": 60
    }
  }
```

---

## API Versioning

```
/api/v1/ - Current version
/api/v2/ - Future version (when breaking changes needed)

Deprecation policy:
- 6 months notice before deprecation
- 12 months support for deprecated version
- Deprecation header: Deprecation: true, Sunset: 2025-01-01
```

---

## OpenAPI Documentation

```
Swagger UI: https://api.opsit.eu/docs
ReDoc: https://api.opsit.eu/redoc
OpenAPI JSON: https://api.opsit.eu/openapi.json
```

---

## API Client SDKs (Future)

- Python SDK
- JavaScript/TypeScript SDK
- Go SDK
- REST collections (Postman, Insomnia)

---

## GraphQL API (Optional Future)

```
Endpoint: /api/graphql

Example query:
query {
  incidents(status: "open", limit: 10) {
    id
    ticketNumber
    title
    assignedTo {
      fullName
      email
    }
    relatedCI {
      name
      type
    }
  }
}
```
