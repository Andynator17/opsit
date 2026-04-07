# OpsIT Backend - Quick Start Guide

## ✅ What's Already Created

```
backend/
├── requirements.txt          ✅ All Python dependencies
├── .env.example             ✅ Configuration template
├── .gitignore               ✅ Git ignore rules
├── app/
│   ├── __init__.py          ✅ Package init
│   ├── core/
│   │   ├── config.py        ✅ Settings & configuration
│   │   ├── database.py      ✅ Database connection
│   │   └── security.py      ✅ Password hashing & JWT
│   └── models/
│       ├── base.py          ✅ Base model mixin
│       ├── tenant.py        ✅ Tenant model
│       ├── company.py       ✅ Company model (multi-company!)
│       └── user.py          ✅ User model
```

## 🚀 Installation Steps

### Step 1: Install Dependencies (5 minutes)

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (2 minutes)

```bash
# Copy example .env
copy .env.example .env  # Windows
# or: cp .env.example .env  # Mac/Linux

# Edit .env with your actual values
notepad .env
```

**Important: Update these in .env:**
```env
DATABASE_URL=postgresql+asyncpg://opsit:YOUR_PASSWORD@localhost:5432/opsit_dev
SECRET_KEY=generate-a-random-32-character-secret-key-here
```

### Step 3: Setup Database (5 minutes)

```bash
# Initialize Alembic (database migrations)
alembic init alembic

# This creates:
# alembic/
# ├── env.py
# ├── script.py.mako
# └── versions/
# alembic.ini
```

**Edit `alembic/env.py`** - Replace the imports section with:
```python
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import your app config and models
from app.core.config import settings
from app.core.database import Base
from app.models import Tenant, Company, User  # Import all models

# this is the Alembic Config object
config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ... rest of env.py (keep the async functions)
```

**Create first migration:**
```bash
alembic revision --autogenerate -m "Initial schema - tenants, companies, users"

# Apply migration
alembic upgrade head
```

**Verify tables created:**
```bash
psql -U opsit -d opsit_dev -c "\dt"

# You should see:
# tenants
# companies
# users
```

### Step 4: Create Main App (I'll generate this for you!)

I'll create the remaining files in the next message:
- app/main.py (FastAPI app)
- app/core/dependencies.py (get_current_user)
- app/schemas/* (Pydantic models)
- app/api/v1/auth.py (login endpoint)

## 📝 What You'll Be Able to Do

After completing setup:

1. ✅ **Start API server**: `uvicorn app.main:app --reload`
2. ✅ **Access docs**: http://localhost:8000/docs
3. ✅ **Login**: POST /api/v1/auth/login
4. ✅ **Create users**: POST /api/v1/auth/register
5. ✅ **Protected endpoints**: With JWT authentication

## 🎯 Next Steps

Once I create the remaining files, you'll run:

```bash
# 1. Create first admin user (seed script)
python -m app.scripts.seed_admin

# 2. Start server
uvicorn app.main:app --reload --port 8000

# 3. Test login at http://localhost:8000/docs
# Use: admin@opsit.local / Admin123!
```

## 📊 Project Status

- ✅ Configuration & Settings
- ✅ Database Connection
- ✅ Security (Argon2 + JWT)
- ✅ Models (Tenant, Company, User)
- ⏳ Schemas (Pydantic) - **Coming next!**
- ⏳ API Endpoints - **Coming next!**
- ⏳ Main App - **Coming next!**

**Ready for the next batch of files? Let me know and I'll create:**
1. Main FastAPI app with CORS
2. Authentication endpoints (login/register)
3. Pydantic schemas
4. Dependencies (get_current_user)
5. Seed script for first admin user

Type "continue" and I'll generate these!
