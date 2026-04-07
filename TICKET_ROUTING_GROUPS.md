# OpsIT - Support Groups & Ticket Routing

## Overview
OpsIT uses **Support Groups** (assignment groups) for intelligent ticket routing, workload distribution, and specialized support team management.

---

## Support Groups Table Structure

### groups
```sql
CREATE TABLE groups (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES companies(id), -- ADDED: for multi-company

    -- Group Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(50) NOT NULL DEFAULT 'support_team',
    -- support_team, approval_group, department, escalation_group

    -- Contact
    email VARCHAR(255), -- group email (e.g., network-ops@company.com)

    -- Management
    manager_id UUID REFERENCES users(id),
    parent_group_id UUID REFERENCES groups(id), -- hierarchical groups

    -- Routing & Assignment
    assignment_rules JSONB, -- automation rules for ticket assignment
    assignment_method VARCHAR(50) DEFAULT 'round_robin',
    -- round_robin, load_balanced, skill_based, manual

    -- Working Hours
    business_hours JSONB,
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- SLA
    default_sla_id UUID REFERENCES slas(id),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### group_members
```sql
CREATE TABLE group_members (
    id UUID PRIMARY KEY,
    group_id UUID NOT NULL REFERENCES groups(id),
    user_id UUID NOT NULL REFERENCES users(id),

    -- Member Role
    role_in_group VARCHAR(50) DEFAULT 'member',
    -- member, leader, backup, approver

    -- Assignment Priority
    assignment_priority INTEGER DEFAULT 1, -- 1 = highest priority
    max_concurrent_tickets INTEGER DEFAULT 10,
    current_ticket_count INTEGER DEFAULT 0, -- updated in real-time

    -- Skills (for skill-based routing)
    skills JSONB, -- ["network", "database", "windows"]
    skill_level INTEGER DEFAULT 1, -- 1-5 scale

    -- Availability
    is_available BOOLEAN DEFAULT TRUE,
    out_of_office_until TIMESTAMPTZ,

    joined_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_group_member UNIQUE (group_id, user_id)
);
```

---

## Common Support Group Types

### 1. Level-Based Groups (ITIL Standard)

**L1 - Service Desk / Helpdesk**
```
Group: Service Desk
Members: Helpdesk agents (10-15 people)
Responsibilities:
- First point of contact
- Incident logging
- Basic troubleshooting
- Password resets
- User account issues
- Ticket categorization
- Route to specialized teams

Assignment: Round-robin (distribute evenly)
Working Hours: 24/7 or business hours
SLA: Response in 15 minutes
```

**L2 - Technical Support Teams**
```
Specialized teams by technology:

├── Network Operations
│   ├── Network engineers
│   ├── Handle: Network issues, connectivity, firewall
│   └── Assignment: Skill-based (network expertise)
│
├── Server Operations
│   ├── System administrators
│   ├── Handle: Server issues, OS problems, performance
│   └── Assignment: Load-balanced
│
├── Database Team
│   ├── Database administrators
│   ├── Handle: Database issues, queries, performance
│   └── Assignment: Skill-based (SQL, Oracle, MongoDB)
│
├── Application Support
│   ├── Application specialists
│   ├── Handle: Application bugs, errors, integrations
│   └── Assignment: Skill-based (by application)
│
└── Desktop Support
    ├── Desktop technicians
    ├── Handle: Hardware, software, peripherals
    └── Assignment: Round-robin
```

**L3 - Expert / Engineering Teams**
```
Group: L3 Engineering
Members: Senior engineers, architects
Responsibilities:
- Complex issues escalated from L2
- Root cause analysis
- Architecture changes
- Vendor escalations

Assignment: Manual (manager assigns)
Working Hours: Business hours only
SLA: Response in 4 hours
```

### 2. Functional Groups

**By Business Function:**
```
├── HR Support Team
│   └── HR-related requests (onboarding, offboarding, benefits)
│
├── Finance IT Team
│   └── Finance systems, ERP, accounting software
│
├── Sales Support Team
│   └── CRM, sales tools, customer-facing systems
│
└── Executive Support
    └── VIP users, executives (priority support)
```

### 3. Regional Groups (for Global Companies)

**By Geography:**
```
├── EMEA Support Team (Europe, Middle East, Africa)
│   ├── Working Hours: 9am-6pm CET
│   └── Languages: English, German, French
│
├── AMER Support Team (Americas)
│   ├── Working Hours: 9am-6pm EST
│   └── Languages: English, Spanish, Portuguese
│
└── APAC Support Team (Asia-Pacific)
    ├── Working Hours: 9am-6pm SGT
    └── Languages: English, Chinese, Japanese
```

---

## Ticket Routing Strategies

### 1. Round-Robin Assignment

**How it works:**
- Tickets distributed evenly among available team members
- Ensures fair workload distribution
- No one gets overloaded

**Example:**
```
Group: Service Desk (5 agents)
Incoming tickets:
1. Ticket #1001 → Agent A
2. Ticket #1002 → Agent B
3. Ticket #1003 → Agent C
4. Ticket #1004 → Agent D
5. Ticket #1005 → Agent E
6. Ticket #1006 → Agent A (cycle repeats)
```

**Configuration:**
```json
{
  "assignment_method": "round_robin",
  "skip_unavailable": true,
  "skip_out_of_office": true
}
```

**Best for:** Service desk, general support teams

---

### 2. Load-Balanced Assignment

**How it works:**
- Assign to agent with fewest open tickets
- Prevents workload imbalance
- Considers agent capacity

**Example:**
```
Group: Application Support
Agent A: 5 open tickets
Agent B: 8 open tickets
Agent C: 3 open tickets

New ticket → Assigned to Agent C (least loaded)
```

**Configuration:**
```json
{
  "assignment_method": "load_balanced",
  "consider_priority": true,
  "max_tickets_per_agent": 15,
  "balance_by": "open_tickets" // or "ticket_priority_weight"
}
```

**Best for:** Technical support teams with varying ticket complexity

---

### 3. Skill-Based Routing

**How it works:**
- Match ticket requirements to agent skills
- Route complex issues to specialists
- Improves first-time resolution rate

**Example:**
```
Incident: "Oracle Database connection error"
Required skills: ["database", "oracle"]

Group: Database Team
├── Agent A: skills=["database", "mysql"], skill_level=3
├── Agent B: skills=["database", "oracle"], skill_level=4 ✓
└── Agent C: skills=["database", "postgresql"], skill_level=3

Ticket → Assigned to Agent B (has Oracle expertise)
```

**Configuration:**
```json
{
  "assignment_method": "skill_based",
  "required_skills": ["database", "oracle"],
  "minimum_skill_level": 3,
  "fallback_method": "load_balanced"
}
```

**Skills Table:**
```sql
-- In group_members table
skills JSONB: {
  "network": {"level": 4, "certifications": ["CCNA"]},
  "database": {"level": 5, "certifications": ["OCP"]},
  "windows": {"level": 3}
}
```

**Best for:** Specialized technical teams

---

### 4. Priority-Based Assignment

**How it works:**
- Critical/VIP tickets go to senior agents
- Low priority to junior agents
- Ensures important issues get expert attention

**Example:**
```
Critical Incident (VIP user)
→ Route to Senior Agent (Leader role)

Low Priority Request
→ Route to Junior Agent (Member role)
```

**Configuration:**
```json
{
  "assignment_method": "priority_based",
  "rules": [
    {
      "ticket_priority": "critical",
      "assign_to_role": "leader"
    },
    {
      "ticket_priority": "high",
      "assign_to_role": "member",
      "minimum_experience": "2_years"
    },
    {
      "ticket_priority": "low",
      "assign_to_role": "member"
    }
  ]
}
```

**Best for:** Mixed-skill teams

---

### 5. Manual Assignment

**How it works:**
- Manager or team lead manually assigns tickets
- No automation
- Full control over distribution

**Example:**
```
New Ticket → Added to team queue (unassigned)
Manager reviews → Assigns to specific agent based on:
- Agent availability
- Agent expertise
- Current workload
- Customer preference
```

**Best for:** Small teams, complex issues, L3 support

---

## Automatic Routing Rules

### Category-Based Routing

```json
{
  "routing_rules": [
    {
      "condition": {
        "category": "Network",
        "urgency": "high"
      },
      "route_to_group": "Network Operations",
      "assignment_method": "skill_based"
    },
    {
      "condition": {
        "category": "Hardware",
        "location": "Building A"
      },
      "route_to_group": "Desktop Support Team A",
      "assignment_method": "round_robin"
    },
    {
      "condition": {
        "keywords": ["database", "sql", "oracle"],
        "priority": "critical"
      },
      "route_to_group": "Database Team",
      "assignment_method": "load_balanced"
    }
  ]
}
```

### Business Hours Routing

```json
{
  "routing_rules": [
    {
      "condition": {
        "time": "business_hours"
      },
      "route_to_group": "EMEA Support Team"
    },
    {
      "condition": {
        "time": "after_hours"
      },
      "route_to_group": "24/7 On-Call Team"
    }
  ]
}
```

### VIP User Routing

```json
{
  "routing_rules": [
    {
      "condition": {
        "user_is_vip": true
      },
      "route_to_group": "Executive Support",
      "assignment_method": "priority_based",
      "assign_to_role": "leader",
      "sla_override": "VIP SLA"
    }
  ]
}
```

---

## Escalation Groups

### Hierarchical Escalation

```
L1 Service Desk
    ↓ (if unresolved in 2 hours)
L2 Technical Team
    ↓ (if unresolved in 4 hours)
L3 Engineering Team
    ↓ (if unresolved in 8 hours)
Vendor Support / Management
```

**Escalation Rules:**
```json
{
  "escalation_rules": [
    {
      "trigger": "sla_breach_warning",
      "percent_remaining": 20,
      "action": "notify_manager"
    },
    {
      "trigger": "unresolved_time",
      "hours": 4,
      "action": "escalate_to_group",
      "target_group": "L2 Technical Team"
    },
    {
      "trigger": "priority",
      "priority": "critical",
      "unresolved_hours": 2,
      "action": "escalate_to_group",
      "target_group": "L3 Engineering"
    }
  ]
}
```

---

## Group Workload Management

### Real-Time Capacity Tracking

```sql
-- Update on ticket assignment
UPDATE group_members
SET current_ticket_count = current_ticket_count + 1
WHERE user_id = 'assigned-agent-uuid';

-- Check agent capacity before assignment
SELECT user_id, current_ticket_count
FROM group_members
WHERE group_id = 'group-uuid'
  AND is_available = TRUE
  AND current_ticket_count < max_concurrent_tickets
  AND (out_of_office_until IS NULL OR out_of_office_until < NOW())
ORDER BY current_ticket_count ASC
LIMIT 1;
```

### Group Statistics Dashboard

```
Group: Network Operations
├── Total Members: 8
├── Available Now: 6
├── Out of Office: 2
├── Open Tickets: 45
├── Average per Agent: 7.5
├── SLA Compliance: 94%
├── Average Resolution Time: 3.2 hours
└── Workload Distribution:
    ├── Agent A: 12 tickets (overloaded)
    ├── Agent B: 8 tickets
    ├── Agent C: 6 tickets
    ├── Agent D: 5 tickets
    ├── Agent E: 4 tickets
    └── Agent F: 10 tickets
```

---

## API Endpoints for Groups

### Group Management

```
GET    /api/v1/groups                    # List all groups
POST   /api/v1/groups                    # Create group
GET    /api/v1/groups/{id}               # Get group details
PATCH  /api/v1/groups/{id}               # Update group
DELETE /api/v1/groups/{id}               # Delete group

GET    /api/v1/groups/{id}/members       # List group members
POST   /api/v1/groups/{id}/members       # Add member
DELETE /api/v1/groups/{id}/members/{user_id}  # Remove member

GET    /api/v1/groups/{id}/queue         # Get group ticket queue
GET    /api/v1/groups/{id}/stats         # Get group statistics
```

### Ticket Assignment

```
POST   /api/v1/incidents/{id}/assign-to-group
POST   /api/v1/incidents/{id}/reassign-to-group
POST   /api/v1/incidents/{id}/escalate-to-group
```

---

## Typical Group Setup for MVP

### Example: Small Company (50-100 employees)

```
Groups:
├── Service Desk (5 agents)
│   ├── Assignment: Round-robin
│   ├── Hours: 9am-5pm Mon-Fri
│   └── Handles: All initial incidents/requests
│
├── IT Operations (3 engineers)
│   ├── Assignment: Load-balanced
│   ├── Hours: 9am-5pm Mon-Fri
│   └── Handles: Escalated technical issues
│
└── IT Manager (1 manager)
    ├── Assignment: Manual
    └── Handles: Approvals, critical issues
```

### Example: MSP with Multiple Customers

```
Groups:
├── Customer A Support Team
│   ├── Members: 3 dedicated agents
│   ├── Assignment: Round-robin
│   └── Company filter: Customer A only
│
├── Customer B Support Team
│   ├── Members: 2 dedicated agents
│   ├── Assignment: Load-balanced
│   └── Company filter: Customer B only
│
├── Shared Technical Team
│   ├── Members: 5 specialists
│   ├── Assignment: Skill-based
│   └── Handles: Complex issues from all customers
│
└── Network Specialists
    ├── Members: 2 network engineers
    ├── Assignment: Manual
    └── Handles: Network issues only (all customers)
```

---

## Group Assignment Workflow

### Automatic Assignment Flow

```
1. User creates incident
   ↓
2. System checks routing rules
   - Category = "Network" → Network Operations Group
   ↓
3. System checks group assignment method
   - Method = "skill_based"
   ↓
4. System finds available agents
   - Query group_members where is_available = true
   - Filter by required skills
   ↓
5. System assigns to best match
   - Agent with matching skills + lowest workload
   ↓
6. Notification sent to agent
   ↓
7. Ticket appears in agent's queue
```

### Manual Assignment by Helpdesk

```
1. Helpdesk agent reviews new ticket
   ↓
2. Determines appropriate group
   - "This looks like a database issue"
   ↓
3. Assigns to group (not specific agent)
   - Assigns to "Database Team"
   ↓
4. Group queue updated
   - Ticket appears in Database Team queue
   ↓
5. Database team member picks up ticket
   - "Assign to me" button
   ↓
6. Ticket removed from group queue
```

---

## Best Practices

### 1. Group Sizing
- **Small teams (2-5 members)**: Manual or round-robin
- **Medium teams (6-15 members)**: Load-balanced or skill-based
- **Large teams (15+ members)**: Sub-groups by specialization

### 2. Assignment Methods
- **Service Desk**: Round-robin (fair distribution)
- **Technical Teams**: Load-balanced or skill-based
- **Specialized Teams**: Skill-based
- **Management**: Manual

### 3. Workload Limits
- Set `max_concurrent_tickets` per agent (e.g., 10-15)
- Monitor and adjust based on ticket complexity
- Prevent burnout by balancing workload

### 4. Skills Management
- Keep skills up to date
- Regular skill assessments
- Training for new technologies

### 5. Escalation Paths
- Define clear escalation criteria
- Time-based (e.g., after 4 hours)
- SLA-based (e.g., at 80% SLA consumed)
- Complexity-based (e.g., requires senior expertise)

---

## Summary

**Support Groups in OpsIT:**
✅ Flexible group structure (L1, L2, L3, functional, regional)
✅ Multiple assignment methods (round-robin, load-balanced, skill-based, manual)
✅ Automatic routing based on rules
✅ Real-time workload tracking
✅ Hierarchical escalation
✅ Multi-company support (MSP use case)

**Key Features:**
- `groups` table with assignment_rules JSONB
- `group_members` table with skills and capacity
- Both incidents and requests have `assigned_group_id`
- Automatic assignment based on configurable rules
- Real-time capacity management

**This enables:**
- Efficient ticket routing
- Balanced workload distribution
- Specialized team handling
- Faster resolution times
- Better SLA compliance

**You're all set for intelligent ticket routing! 🎯**
