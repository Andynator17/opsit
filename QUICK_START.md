# 🚀 OpsIT RBAC System - Quick Start Guide

## ✅ What's Ready

### Backend
- ✅ FastAPI server running at http://localhost:8000
- ✅ Database migrated with RBAC tables
- ✅ 30 default roles seeded
- ✅ All API endpoints working

### Frontend
- ✅ Navigation restructured into 3 sections
- ✅ Roles management page
- ✅ Permission Groups management page
- ✅ Routes configured

---

## 🏃 Start the Frontend

### Option 1: Start Frontend Dev Server
```bash
cd frontend
npm run dev
```

The frontend will start at: http://localhost:5173

### Option 2: If already running
If you already have the frontend running, it should auto-reload with the new changes.

---

## 🎯 Test the RBAC System

### 1. Access the Application
1. Open http://localhost:5173
2. Login with your admin credentials

### 2. Navigate to Roles
1. Click the **hamburger menu** (if sidebar is collapsed)
2. Scroll down to **"Configuration & Development"** section
3. Click **"Roles"**
4. You should see all 30 seeded roles!

**Try this:**
- Filter by module (select "incident" from dropdown)
- View role details
- Create a custom role (click "Create Custom Role")
- Edit a custom role
- Notice system roles are protected (cannot edit/delete)

### 3. Navigate to Permission Groups
1. In the sidebar, still in **"Configuration & Development"**
2. Click **"Permission Groups"**

**Try this:**
- Create a permission group (e.g., "Helpdesk Team")
- Click "Manage Roles" → Add roles (Incident Agent, Request Agent)
- Click "Manage Members" → Add your user
- View the group showing members and roles

### 4. Explore the New Navigation
The navigation is now organized in **3 sections**:

#### 📋 Fulfillment
- Dashboard ✓
- Incident Management ✓
- Request Management ✓
- IT-Change Management (placeholder)
- Problem Management (placeholder)
- Service Management (placeholder)
- Event Management (placeholder)
- Asset Management (placeholder)
- Configuration Management (placeholder)
- CMDB (placeholder)
- SLA (placeholder)
- HR Management (placeholder)
- Business Case Management (placeholder)

#### 🏢 Foundation
- Companies ✓
- Departments (placeholder)
- Location (placeholder)
- User ✓
- Support Groups (placeholder)
- Services (placeholder)
- Sold Products (placeholder)
- Install Bases (placeholder)
- Contracts (placeholder)

#### ⚙️ Configuration & Development
- Server Scripts (placeholder)
- Client Scripts (placeholder)
- Workflow Editor (placeholder)
- Custom Apps (placeholder)
- Notifications (placeholder)
- Rest API Explorer (placeholder)
- **Permission Groups** ✅ NEW!
- **Roles** ✅ NEW!
- ACL (placeholder)
- Logs (placeholder)
- System Properties (placeholder)

---

## 🔑 Default Roles Available

You have 30 roles across 9 modules:

### Incident (4 roles)
- Incident Read
- Incident Read & Create
- Incident Agent
- Incident Admin

### Request (4 roles)
- Request Read
- Request Read & Create
- Request Agent
- Request Admin

### User (4 roles)
- User Read
- User Read & Create
- User Agent
- User Admin

### Company (4 roles)
- Company Read
- Company Read & Create
- Company Agent
- Company Admin

### Support Group (4 roles)
- Support Group Read
- Support Group Read & Create
- Support Group Agent
- Support Group Admin

### Category (4 roles)
- Category Read
- Category Read & Create
- Category Agent
- Category Admin

### Dashboard (2 roles)
- Dashboard View
- Dashboard Admin

### Role (2 roles)
- Role Read
- Role Admin

### Permission Group (2 roles)
- Permission Group Read
- Permission Group Admin

---

## 📚 API Endpoints

All endpoints are documented at:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### Roles Endpoints
```
GET    /api/v1/roles                 - List all roles
GET    /api/v1/roles/{id}            - Get role by ID
POST   /api/v1/roles                 - Create custom role
PATCH  /api/v1/roles/{id}            - Update role
DELETE /api/v1/roles/{id}            - Delete role
```

### Permission Groups Endpoints
```
GET    /api/v1/permission-groups                           - List all groups
GET    /api/v1/permission-groups/{id}                      - Get group by ID
POST   /api/v1/permission-groups                           - Create group
PATCH  /api/v1/permission-groups/{id}                      - Update group
DELETE /api/v1/permission-groups/{id}                      - Delete group
POST   /api/v1/permission-groups/{id}/members              - Add members
DELETE /api/v1/permission-groups/{id}/members/{user_id}    - Remove member
POST   /api/v1/permission-groups/{id}/roles                - Add roles
DELETE /api/v1/permission-groups/{id}/roles/{role_id}      - Remove role
```

---

## 🎨 Screenshots of What You'll See

### Roles Page
- Table with all roles
- Filter by module dropdown
- Statistics cards (Total, System, Custom)
- Color-coded level tags
- Create/Edit/Delete buttons
- System roles are protected

### Permission Groups Page
- Table with all groups
- Member count and role count
- Create/Edit/Delete buttons
- "Manage Members" and "Manage Roles" buttons
- Modal dialogs for member/role management

---

## 💡 Usage Example

### Scenario: Create a "Helpdesk Team"

1. **Create Permission Group**
   - Navigate to "Permission Groups"
   - Click "Create Permission Group"
   - Name: "Helpdesk Agent"
   - Description: "Standard helpdesk agent permissions"
   - Click OK

2. **Add Roles**
   - Click "Manage Roles" on the new group
   - Select roles:
     - Incident Agent
     - Request Agent
     - Dashboard View
   - Click OK

3. **Add Members**
   - Click "Manage Members"
   - Select users (John Doe, Jane Smith)
   - Click OK

4. **Result**
   - John and Jane can now:
     - View, create, update, assign, and resolve incidents
     - View, create, update, approve, and resolve requests
     - View dashboards
   - All from being in ONE permission group!

---

## 🐛 Troubleshooting

### Frontend doesn't compile
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev
```

### Backend not responding
Check if the backend is running at http://localhost:8000/health

### Can't see new menu items
- Hard refresh the browser (Ctrl+F5)
- Clear browser cache
- Check browser console for errors

### System roles won't edit
This is expected! System roles are protected and cannot be modified or deleted.

---

## 📖 Documentation

- **Backend RBAC Testing**: [RBAC_TESTING.md](./RBAC_TESTING.md)
- **Support Groups API**: [SUPPORT_GROUPS_API.md](./SUPPORT_GROUPS_API.md)
- **Frontend Updates**: [FRONTEND_UPDATES.md](./FRONTEND_UPDATES.md)

---

## ✨ What's Working

✅ Complete RBAC backend
✅ 30 default roles seeded
✅ Permission checking utilities
✅ Roles management UI
✅ Permission Groups management UI
✅ 3-section navigation
✅ All API endpoints
✅ Full member/role assignment
✅ Backend + Frontend integrated

---

## 🎉 You're Ready!

Everything is implemented and ready to use. Just start the frontend dev server and explore the new RBAC system!

```bash
cd frontend
npm run dev
```

Then navigate to http://localhost:5173 and login! 🚀
