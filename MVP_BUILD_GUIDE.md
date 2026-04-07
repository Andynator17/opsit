# OpsIT - MVP Build Guide

## What You Need to Build the MVP

This guide outlines EXACTLY what you need to build OpsIT MVP in **12 weeks**.

---

## Prerequisites

### 1. Development Environment

**Required Software:**
```bash
# Core Tools
- Python 3.11+ (backend)
- Node.js 20+ & npm (frontend)
- PostgreSQL 16 (database)
- Redis 7+ (cache & queue)
- Git (version control)
- Docker Desktop (containerization)

# Code Editors
- VS Code (recommended)
  - Extensions: Python, Pylance, ESLint, Prettier, Docker

# Optional but Recommended
- DBeaver or pgAdmin (database GUI)
- Postman or Insomnia (API testing)
- GitHub Desktop or GitKraken (git GUI)
```

**Operating System:**
- Windows 10/11 (WSL2 for Docker)
- macOS 12+
- Linux (Ubuntu 22.04+)

### 2. Team Composition (Minimum)

**Option 1: Small Team (Recommended)**
- 1 Backend Developer (Python/FastAPI)
- 1 Frontend Developer (React/TypeScript)
- 0.5 DevOps (part-time for Docker setup)

**Option 2: Solo Developer**
- Full-stack developer (you!)
- Timeline: 6 months instead of 3 months

### 3. Accounts & Services

**Required:**
- GitHub account (code hosting)
- Email service (SendGrid free tier or Gmail SMTP)
- Cloud provider (AWS, Azure, or DigitalOcean - free tiers available)

**Optional (for production):**
- Domain name (e.g., opsit.io)
- SSL certificate (Let's Encrypt - free)
- Monitoring service (Sentry free tier)

---

## MVP Scope Reminder

**What We're Building (12 weeks):**
✅ Incident Management
✅ Request Management & Service Catalog
✅ User Management (with RBAC)
✅ Company Management (multi-company foundation)
✅ Self-Service Portal
✅ Basic SLA Tracking
✅ Dashboard & Basic Reports
✅ Knowledge Base (read-only)
✅ Email Notifications

**What We're NOT Building (Phase 2+):**
❌ CMDB (Configuration Items)
❌ Problem Management
❌ Change Management
❌ Advanced Workflows
❌ SSO/SAML
❌ Mobile App
❌ Advanced Analytics

---

## Technology Stack (Confirmed)

### Backend
```
Framework:      FastAPI 0.110+
ORM:            SQLAlchemy 2.0 (async)
Database:       PostgreSQL 16
Migration:      Alembic
Auth:           python-jose (JWT)
Password:       passlib[argon2]
Tasks:          Celery
Cache:          Redis
Email:          aiosmtplib
Validation:     Pydantic v2
Testing:        pytest, pytest-asyncio
```

### Frontend
```
Framework:      React 18.2+
Language:       TypeScript 5+
Build:          Vite 5+
UI Library:     Ant Design 5+ or Shadcn/UI
State:          Zustand 4+
Routing:        React Router 6+
Forms:          React Hook Form + Zod
API Client:     Axios + TanStack Query
Testing:        Vitest + React Testing Library
```

### DevOps
```
Containers:     Docker + Docker Compose
Proxy:          Nginx
Version:        Git + GitHub
CI/CD:          GitHub Actions (optional for MVP)
```

---

## Step-by-Step Build Process

## Phase 1: Project Setup (Week 1)

### Step 1.1: Initialize Git Repository

```bash
# Create project directory
mkdir opsit
cd opsit

# Initialize git
git init
git branch -M main

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
*.db
*.sqlite3

# Node
node_modules/
dist/
build/
.DS_Store

# IDE
.vscode/
.idea/
*.swp

# Docker
*.log
EOF

# Initial commit
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
gh repo create opsit --private --source=. --remote=origin
git push -u origin main
```

### Step 1.2: Create Project Structure

```bash
# Create directory structure
mkdir -p backend/{app/{api/v1,core,models,schemas,services,repositories,tasks,utils,tests},alembic/versions,scripts}
mkdir -p frontend/{src/{api,components,pages,hooks,store,routes,types,utils,styles,config},public}
mkdir -p docker/{backend,frontend,nginx,postgres}
mkdir -p docs
```

### Step 1.3: Initialize Backend (Python/FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Or (Linux/Mac)
source .venv/bin/activate

# Create requirements files
cat > requirements/base.txt << EOF
# FastAPI
fastapi==0.110.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[argon2]==1.7.4
python-multipart==0.0.6

# Pydantic
pydantic==2.6.0
pydantic-settings==2.1.0

# Redis & Celery
redis==5.0.1
celery==5.3.6

# Email
aiosmtplib==3.0.1
jinja2==3.1.3

# Utils
python-dotenv==1.0.0
httpx==0.26.0
EOF

cat > requirements/dev.txt << EOF
-r base.txt

# Testing
pytest==8.0.0
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Linting
ruff==0.1.14
black==24.1.1
mypy==1.8.0

# Development
ipython==8.20.0
EOF

# Install dependencies
pip install -r requirements/dev.txt

# Create .env file
cat > .env << EOF
# Application
PROJECT_NAME=OpsIT
VERSION=1.0.0
API_V1_PREFIX=/api/v1
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://opsit:opsit_dev@localhost:5432/opsit_dev

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email (use Gmail SMTP for testing)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@opsit.io

# Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
EOF

echo "✅ Backend initialized!"
```

### Step 1.4: Initialize Frontend (React/TypeScript)

```bash
cd ../frontend

# Create Vite project
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Install additional libraries
npm install \
  antd \
  @ant-design/icons \
  axios \
  @tanstack/react-query \
  zustand \
  react-router-dom \
  react-hook-form \
  zod \
  @hookform/resolvers \
  dayjs

# Install dev dependencies
npm install -D \
  @types/node \
  @vitejs/plugin-react \
  eslint \
  prettier \
  vitest \
  @testing-library/react \
  @testing-library/jest-dom

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=OpsIT
VITE_APP_VERSION=1.0.0
EOF

echo "✅ Frontend initialized!"
```

### Step 1.5: Setup Docker Compose (Development)

```bash
cd ..

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: opsit_postgres
    environment:
      POSTGRES_USER: opsit
      POSTGRES_PASSWORD: opsit_dev
      POSTGRES_DB: opsit_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U opsit"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: opsit_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Uncomment when backend is ready
  # backend:
  #   build:
  #     context: ./backend
  #     dockerfile: Dockerfile
  #   container_name: opsit_backend
  #   environment:
  #     DATABASE_URL: postgresql+asyncpg://opsit:opsit_dev@postgres:5432/opsit_dev
  #     REDIS_URL: redis://redis:6379/0
  #   volumes:
  #     - ./backend:/app
  #   ports:
  #     - "8000:8000"
  #   depends_on:
  #     postgres:
  #       condition: service_healthy
  #   command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Uncomment when frontend is ready
  # frontend:
  #   build:
  #     context: ./frontend
  #     dockerfile: Dockerfile
  #   container_name: opsit_frontend
  #   environment:
  #     VITE_API_URL: http://localhost:8000/api/v1
  #   volumes:
  #     - ./frontend:/app
  #     - /app/node_modules
  #   ports:
  #     - "5173:5173"
  #   command: npm run dev -- --host 0.0.0.0

volumes:
  postgres_data:
  redis_data:
EOF

# Start only database services for now
docker-compose up -d postgres redis

echo "✅ Docker services started!"
```

---

## Phase 2: Backend Foundation (Week 1-2)

### Step 2.1: Create Core Configuration

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "OpsIT"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Redis
    REDIS_URL: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str = "noreply@opsit.io"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### Step 2.2: Setup Database Connection

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Step 2.3: Initialize Alembic (Database Migrations)

```bash
cd backend

# Initialize Alembic
alembic init alembic

# Edit alembic.ini - change sqlalchemy.url to:
# sqlalchemy.url = postgresql+asyncpg://opsit:opsit_dev@localhost:5432/opsit_dev

# Or better: use environment variable
# Comment out the line: sqlalchemy.url = ...
```

```python
# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import your models
from app.core.config import settings
from app.core.database import Base
from app.models import *  # Import all models

# this is the Alembic Config object
config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Step 2.4: Create First Models

```python
# backend/app/models/__init__.py
from .tenant import Tenant
from .company import Company
from .user import User
from .incident import Incident
from .request import Request

__all__ = ["Tenant", "Company", "User", "Incident", "Request"]
```

```python
# backend/app/models/base.py
from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class BaseModel:
    """Base model with common fields"""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
```

```python
# backend/app/models/tenant.py
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from .base import BaseModel

class Tenant(Base, BaseModel):
    __tablename__ = "tenants"

    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default='active')
    plan = Column(String(50), nullable=False, default='starter')
    max_users = Column(Integer, default=10)
    max_storage_gb = Column(Integer, default=10)
    custom_domain = Column(String(255))
    branding = Column(JSONB)
    settings = Column(JSONB)
    subscription_ends_at = Column(TIMESTAMP(timezone=True))
```

Continue with Company, User models following DATABASE_SCHEMA.md...

### Step 2.5: Create First Migration

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Verify tables created
psql -U opsit -d opsit_dev -c "\dt"
```

---

## Phase 3: Authentication (Week 2)

### Step 3.1: Security Utilities

```python
# backend/app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### Step 3.2: Auth Endpoints

```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.auth import Token, TokenResponse
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Authenticate user
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        }
    }
```

---

## Phase 4: Core APIs (Week 3-7)

Follow this pattern for each module:
1. Create SQLAlchemy model
2. Create Pydantic schemas (request/response)
3. Create repository (data access layer)
4. Create service (business logic)
5. Create API endpoints
6. Write tests

**Priority Order:**
1. Users & Auth (Week 2)
2. Companies & Departments (Week 3)
3. Incidents (Week 4-5)
4. Requests & Catalog (Week 6-7)
5. SLA & Dashboard (Week 8)

---

## Phase 5: Frontend Foundation (Week 2-3)

### Step 5.1: Setup Routing

```typescript
// frontend/src/routes/index.tsx
import { createBrowserRouter } from 'react-router-dom';
import LoginPage from '@/pages/auth/LoginPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import IncidentListPage from '@/pages/incidents/IncidentListPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <PrivateRoute />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'incidents', element: <IncidentListPage /> },
      { path: 'requests', element: <RequestListPage /> },
    ],
  },
]);
```

### Step 5.2: API Client

```typescript
// frontend/src/api/client.ts
import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default client;
```

---

## Testing Strategy

### Backend Tests

```python
# backend/app/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.core.database import Base, get_db

# Test database
TEST_DATABASE_URL = "postgresql+asyncpg://opsit:opsit_test@localhost:5432/opsit_test"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def client(test_engine):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

```python
# backend/app/tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test123!",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
```

### Frontend Tests

```typescript
// frontend/src/components/LoginForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import LoginForm from './LoginForm';

describe('LoginForm', () => {
  it('renders login form', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('submits form with credentials', async () => {
    render(<LoginForm />);
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Test123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    // Assert API call was made
  });
});
```

---

## Development Workflow

### Daily Workflow

```bash
# 1. Start database services
docker-compose up -d postgres redis

# 2. Start backend (in one terminal)
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000

# 3. Start frontend (in another terminal)
cd frontend
npm run dev

# 4. Access application
# Frontend: http://localhost:5173
# Backend API docs: http://localhost:8000/docs
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/incident-management

# Make changes, commit frequently
git add .
git commit -m "feat: add incident create endpoint"

# Push to GitHub
git push origin feature/incident-management

# Create Pull Request on GitHub
# After review, merge to main
```

---

## MVP Completion Checklist

### Week 12: Final Testing

- [ ] All API endpoints work
- [ ] All UI pages functional
- [ ] User can login
- [ ] User can create incident
- [ ] User can create request
- [ ] Helpdesk can manage tickets
- [ ] SLA tracking works
- [ ] Email notifications sent
- [ ] Tests pass (70%+ coverage)
- [ ] No critical bugs
- [ ] Docker deployment works

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database backed up
- [ ] SSL certificate installed
- [ ] Domain configured
- [ ] Monitoring setup (basic)
- [ ] Documentation written

---

## Estimated Effort (Hours)

| Phase | Backend | Frontend | Total |
|-------|---------|----------|-------|
| Setup | 8h | 4h | 12h |
| Auth | 16h | 12h | 28h |
| Users | 12h | 8h | 20h |
| Companies | 8h | 6h | 14h |
| Incidents | 32h | 24h | 56h |
| Requests | 28h | 20h | 48h |
| SLA | 16h | 8h | 24h |
| Dashboard | 12h | 16h | 28h |
| Portal | 8h | 20h | 28h |
| Testing | 24h | 16h | 40h |
| Deployment | 12h | 8h | 20h |
| **Total** | **176h** | **142h** | **318h** |

**Team of 2 (40h/week each):** ~4 weeks if 100% focused
**Team of 2 (realistic 60% productive time):** ~7-8 weeks
**Solo (40h/week):** ~8 weeks
**Solo (realistic):** ~12 weeks ✅

---

## Summary

**To build MVP, you need:**

1. ✅ Development environment (Python, Node, PostgreSQL, Redis, Docker)
2. ✅ Project structure initialized
3. ✅ Backend foundation (FastAPI, SQLAlchemy, Alembic)
4. ✅ Frontend foundation (React, TypeScript, Ant Design)
5. ✅ Authentication system
6. ✅ Core APIs (Incidents, Requests, Users, Companies)
7. ✅ Frontend pages (Dashboard, Ticket List, Forms)
8. ✅ Basic SLA and notifications
9. ✅ Testing (unit + integration)
10. ✅ Docker deployment

**Time: 12 weeks with 2 developers or 6 months solo**

**Next Steps:**
1. Initialize project structure (today)
2. Setup development environment (1-2 days)
3. Start Week 1: Backend foundation
4. Follow the 12-week roadmap

**You have ALL the documentation you need! Let's start building! 🚀**
