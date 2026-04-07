# 🚀 How to Run OpsIT Backend

## ✅ Complete Setup (First Time)

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Mac/Linux

# Install
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example
copy .env.example .env  # Windows
# or: cp .env.example .env  # Mac/Linux

# Edit .env - update these:
# - DATABASE_URL (your PostgreSQL credentials)
# - SECRET_KEY (generate random 32+ char string)
```

### 3. Setup Database Migrations

```bash
# Initialize Alembic
alembic init alembic
```

**Edit `alembic/env.py`** - Add at the top (after imports):
```python
from app.core.config import settings
from app.core.database import Base
from app.models import Tenant, Company, User

# Set database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata
```

**Create migration:**
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### 4. Seed Initial Data

```bash
# Create tenant, company, and admin user
python -m app.scripts.seed_data

# You should see:
# ✅ Created tenant: OpsIT Demo
# ✅ Created company: Demo Company
# ✅ Created admin user: admin@opsit.local
```

### 5. Start API Server

```bash
uvicorn app.main:app --reload --port 8000

# You should see:
# 🚀 OpsIT API 1.0.0 starting...
# 📚 API Docs: http://localhost:8000/api/v1/docs
```

## 🎯 Test Your API

### Open Interactive Docs
Visit: **http://localhost:8000/api/v1/docs**

### Test Endpoints:

1. **Health Check**
   - GET `/health`
   - Should return: `{"status": "healthy", "database": "connected"}`

2. **Login** (Try it now!)
   - POST `/api/v1/auth/login`
   - Click "Try it out"
   - Fill in:
     ```
     username: admin@opsit.local
     password: Admin123!
     ```
   - Click "Execute"
   - You should get `access_token` and user info!

3. **Get Current User**
   - GET `/api/v1/users/me`
   - Click the lock icon 🔒
   - Paste the `access_token` from login
   - Click "Authorize"
   - Now click "Try it out" → "Execute"
   - You should see your user data!

## 📝 Common Commands

```bash
# Start server (development with auto-reload)
uvicorn app.main:app --reload --port 8000

# Start server (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run seed script
python -m app.scripts.seed_data

# Python shell with database access
python
>>> from app.core.database import AsyncSessionLocal
>>> from app.models import *
```

## 🐛 Troubleshooting

### Problem: "No module named 'app'"
**Solution:** Make sure you're in the `backend` directory and venv is activated

### Problem: "Connection refused" to database
**Solution:** Check PostgreSQL is running and DATABASE_URL in .env is correct

### Problem: "No tenant found"
**Solution:** Run seed script: `python -m app.scripts.seed_data`

### Problem: "Cannot import name 'settings'"
**Solution:** Make sure .env file exists in backend directory

## 📊 What You Have Working

✅ **Authentication**
- Login endpoint with JWT
- Protected endpoints
- Password hashing (Argon2)

✅ **User Management**
- Get current user
- Update user profile
- List users (admin)

✅ **Database**
- PostgreSQL with async SQLAlchemy
- Multi-company support (Tenant → Company → User)
- Migrations with Alembic

✅ **Security**
- JWT tokens (access + refresh)
- Role-based access (admin, agent, user)
- Password hashing

## 🎉 Success!

If you can:
1. ✅ Start the server without errors
2. ✅ See health check as "healthy"
3. ✅ Login at /api/v1/docs
4. ✅ Get current user info

**You're ready to build the rest of OpsIT!** 🚀

## 📚 Next Steps

1. Add Incident endpoints
2. Add Request endpoints
3. Add Company management
4. Build frontend
5. Deploy to production

**Happy coding!** 💻
