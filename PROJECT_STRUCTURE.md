# OpsIT - Project Structure

## Repository Structure

```
opsit/
├── backend/                    # Python/FastAPI backend
│   ├── alembic/               # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry
│   │   ├── core/              # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── config.py      # Configuration management
│   │   │   ├── security.py    # Auth, JWT, password hashing
│   │   │   ├── database.py    # Database connection
│   │   │   ├── dependencies.py # FastAPI dependencies
│   │   │   ├── exceptions.py  # Custom exceptions
│   │   │   └── middleware.py  # Custom middleware
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # Base model class
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── group.py
│   │   │   ├── incident.py
│   │   │   ├── request.py
│   │   │   ├── comment.py
│   │   │   ├── attachment.py
│   │   │   ├── configuration_item.py
│   │   │   ├── service.py
│   │   │   ├── sla.py
│   │   │   ├── knowledge_article.py
│   │   │   ├── workflow.py
│   │   │   ├── notification.py
│   │   │   └── audit_log.py
│   │   ├── schemas/           # Pydantic schemas (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── common.py      # Common schemas (pagination, etc.)
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   ├── incident.py
│   │   │   ├── request.py
│   │   │   ├── comment.py
│   │   │   ├── configuration_item.py
│   │   │   ├── service.py
│   │   │   ├── sla.py
│   │   │   └── knowledge_article.py
│   │   ├── api/               # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py        # Route dependencies
│   │   │   └── v1/            # API version 1
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── groups.py
│   │   │       ├── incidents.py
│   │   │       ├── requests.py
│   │   │       ├── comments.py
│   │   │       ├── attachments.py
│   │   │       ├── catalog.py
│   │   │       ├── cmdb.py
│   │   │       ├── services.py
│   │   │       ├── slas.py
│   │   │       ├── knowledge.py
│   │   │       ├── workflows.py
│   │   │       ├── notifications.py
│   │   │       ├── dashboard.py
│   │   │       ├── reports.py
│   │   │       ├── admin.py
│   │   │       └── audit.py
│   │   ├── services/          # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── incident_service.py
│   │   │   ├── request_service.py
│   │   │   ├── sla_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── workflow_service.py
│   │   │   ├── knowledge_service.py
│   │   │   └── audit_service.py
│   │   ├── repositories/      # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # Base repository
│   │   │   ├── user_repository.py
│   │   │   ├── incident_repository.py
│   │   │   ├── request_repository.py
│   │   │   └── ...
│   │   ├── tasks/             # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── email_tasks.py
│   │   │   ├── notification_tasks.py
│   │   │   ├── sla_tasks.py
│   │   │   └── report_tasks.py
│   │   ├── utils/             # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── email.py
│   │   │   ├── file_storage.py # S3 integration
│   │   │   ├── template_engine.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   ├── tests/             # Tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_incidents.py
│   │   │   ├── test_requests.py
│   │   │   └── ...
│   │   └── websocket/         # WebSocket handlers
│   │       ├── __init__.py
│   │       ├── connection_manager.py
│   │       └── handlers.py
│   ├── scripts/               # Utility scripts
│   │   ├── seed_data.py       # Seed database
│   │   ├── create_admin.py    # Create admin user
│   │   └── migrate_data.py
│   ├── requirements/
│   │   ├── base.txt           # Common dependencies
│   │   ├── dev.txt            # Development dependencies
│   │   └── prod.txt           # Production dependencies
│   ├── .env.example
│   ├── .env
│   ├── pyproject.toml         # Poetry configuration
│   ├── pytest.ini
│   └── Dockerfile
│
├── frontend/                   # React frontend
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── assets/
│   ├── src/
│   │   ├── main.tsx           # Application entry point
│   │   ├── App.tsx
│   │   ├── vite-env.d.ts
│   │   ├── assets/            # Images, fonts, etc.
│   │   ├── components/        # Reusable components
│   │   │   ├── common/        # Common components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   └── ...
│   │   │   ├── layout/        # Layout components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── MainLayout.tsx
│   │   │   ├── forms/         # Form components
│   │   │   │   ├── IncidentForm.tsx
│   │   │   │   ├── RequestForm.tsx
│   │   │   │   ├── UserForm.tsx
│   │   │   │   └── ...
│   │   │   └── widgets/       # Dashboard widgets
│   │   │       ├── StatCard.tsx
│   │   │       ├── TicketList.tsx
│   │   │       ├── SLAWidget.tsx
│   │   │       └── ...
│   │   ├── pages/             # Page components
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── ForgotPasswordPage.tsx
│   │   │   │   └── ResetPasswordPage.tsx
│   │   │   ├── dashboard/
│   │   │   │   └── DashboardPage.tsx
│   │   │   ├── incidents/
│   │   │   │   ├── IncidentListPage.tsx
│   │   │   │   ├── IncidentDetailPage.tsx
│   │   │   │   └── CreateIncidentPage.tsx
│   │   │   ├── requests/
│   │   │   │   ├── RequestListPage.tsx
│   │   │   │   ├── RequestDetailPage.tsx
│   │   │   │   └── CreateRequestPage.tsx
│   │   │   ├── catalog/
│   │   │   │   ├── ServiceCatalogPage.tsx
│   │   │   │   └── CatalogItemPage.tsx
│   │   │   ├── cmdb/
│   │   │   │   ├── CMDBListPage.tsx
│   │   │   │   ├── CIDetailPage.tsx
│   │   │   │   └── CIRelationshipsPage.tsx
│   │   │   ├── knowledge/
│   │   │   │   ├── KnowledgeBasePage.tsx
│   │   │   │   ├── ArticleViewPage.tsx
│   │   │   │   └── CreateArticlePage.tsx
│   │   │   ├── reports/
│   │   │   │   └── ReportsPage.tsx
│   │   │   ├── admin/
│   │   │   │   ├── UsersPage.tsx
│   │   │   │   ├── GroupsPage.tsx
│   │   │   │   ├── SettingsPage.tsx
│   │   │   │   └── AuditLogsPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── features/          # Feature-specific modules
│   │   │   ├── incidents/
│   │   │   │   ├── api/       # API calls
│   │   │   │   ├── hooks/     # Custom hooks
│   │   │   │   ├── types/     # TypeScript types
│   │   │   │   └── utils/     # Feature utilities
│   │   │   ├── requests/
│   │   │   ├── cmdb/
│   │   │   └── ...
│   │   ├── api/               # API client
│   │   │   ├── client.ts      # Axios instance
│   │   │   ├── auth.ts
│   │   │   ├── incidents.ts
│   │   │   ├── requests.ts
│   │   │   ├── users.ts
│   │   │   └── ...
│   │   ├── hooks/             # Global custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useNotifications.ts
│   │   │   └── ...
│   │   ├── store/             # State management (Zustand)
│   │   │   ├── authStore.ts
│   │   │   ├── notificationStore.ts
│   │   │   ├── uiStore.ts
│   │   │   └── ...
│   │   ├── routes/            # Route configuration
│   │   │   ├── index.tsx
│   │   │   ├── PrivateRoute.tsx
│   │   │   └── PublicRoute.tsx
│   │   ├── types/             # TypeScript types
│   │   │   ├── common.ts
│   │   │   ├── incident.ts
│   │   │   ├── request.ts
│   │   │   ├── user.ts
│   │   │   └── ...
│   │   ├── utils/             # Utility functions
│   │   │   ├── date.ts
│   │   │   ├── format.ts
│   │   │   ├── validation.ts
│   │   │   └── constants.ts
│   │   ├── styles/            # Global styles
│   │   │   ├── globals.css
│   │   │   ├── variables.css
│   │   │   └── theme.ts
│   │   └── config/            # Configuration
│   │       ├── api.ts
│   │       └── constants.ts
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── .env.example
│   ├── .env
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js     # If using Tailwind
│   ├── vitest.config.ts
│   └── Dockerfile
│
├── docker/                     # Docker configuration
│   ├── backend/
│   │   └── Dockerfile
│   ├── frontend/
│   │   └── Dockerfile
│   ├── nginx/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   └── postgres/
│       └── init.sql
│
├── docs/                       # Documentation
│   ├── api/                   # API documentation
│   ├── architecture/          # Architecture diagrams
│   ├── deployment/            # Deployment guides
│   ├── user-guide/            # User documentation
│   └── developer-guide/       # Developer documentation
│
├── scripts/                    # Project scripts
│   ├── setup.sh               # Initial setup
│   ├── dev.sh                 # Start development servers
│   ├── test.sh                # Run all tests
│   ├── build.sh               # Build for production
│   └── deploy.sh              # Deployment script
│
├── .github/                    # GitHub Actions
│   └── workflows/
│       ├── ci.yml             # CI pipeline
│       ├── cd.yml             # CD pipeline
│       └── security-scan.yml  # Security scanning
│
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── .gitignore
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

---

## Backend Structure Details

### Core Module (`app/core/`)

#### `config.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "OpsIT"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []

    # Redis
    REDIS_URL: str

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str

    # S3/Storage
    S3_BUCKET: str
    S3_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

#### `security.py`
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

#### `database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### Models (`app/models/`)

#### `base.py`
```python
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class BaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
```

#### `incident.py`
```python
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Incident(Base, BaseModel):
    __tablename__ = "incidents"

    ticket_number = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="new")
    priority = Column(String(50), nullable=False, default="medium")
    urgency = Column(String(50), nullable=False, default="medium")
    impact = Column(String(50), nullable=False, default="medium")

    # Relationships
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

    reported_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reported_by = relationship("User", foreign_keys=[reported_by_id])

    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")

    # JSONB fields
    tags = Column(JSONB, nullable=True)
    custom_fields = Column(JSONB, nullable=True)

    # Indexes defined in migration
```

### Schemas (`app/schemas/`)

#### `incident.py`
```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

class IncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: str = Field(default="medium")
    urgency: str = Field(default="medium")
    impact: str = Field(default="medium")
    category_id: UUID | None = None

class IncidentCreate(IncidentBase):
    custom_fields: dict | None = None

class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_to_id: UUID | None = None

class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_number: str
    status: str
    created_at: datetime
    updated_at: datetime
    assigned_to: "UserResponse | None" = None
    reported_by: "UserResponse"
```

### API Routes (`app/api/v1/`)

#### `incidents.py`
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    status: str | None = None,
    priority: str | None = None,
    assigned_to_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = IncidentService(db)
    return await service.list_incidents(
        tenant_id=current_user.tenant_id,
        status=status,
        priority=priority,
        assigned_to_id=assigned_to_id,
        page=page,
        page_size=page_size
    )

@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = IncidentService(db)
    return await service.create_incident(
        tenant_id=current_user.tenant_id,
        incident=incident,
        user_id=current_user.id
    )

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = IncidentService(db)
    incident = await service.get_incident(incident_id, current_user.tenant_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_update: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = IncidentService(db)
    return await service.update_incident(
        incident_id=incident_id,
        tenant_id=current_user.tenant_id,
        incident_update=incident_update,
        user_id=current_user.id
    )
```

### Services (`app/services/`)

#### `incident_service.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.sla_service import SLAService
from app.services.notification_service import NotificationService

class IncidentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sla_service = SLAService(db)
        self.notification_service = NotificationService(db)

    async def create_incident(
        self,
        tenant_id: UUID,
        incident: IncidentCreate,
        user_id: UUID
    ) -> Incident:
        # Generate ticket number
        ticket_number = await self._generate_ticket_number(tenant_id)

        # Create incident
        db_incident = Incident(
            tenant_id=tenant_id,
            ticket_number=ticket_number,
            reported_by_id=user_id,
            **incident.model_dump()
        )

        self.db.add(db_incident)
        await self.db.commit()
        await self.db.refresh(db_incident)

        # Apply SLA
        await self.sla_service.apply_sla(db_incident)

        # Send notifications
        await self.notification_service.notify_incident_created(db_incident)

        return db_incident

    async def list_incidents(
        self,
        tenant_id: UUID,
        status: str | None = None,
        priority: str | None = None,
        assigned_to_id: UUID | None = None,
        page: int = 1,
        page_size: int = 50
    ):
        query = select(Incident).where(
            Incident.tenant_id == tenant_id,
            Incident.is_deleted == False
        )

        if status:
            query = query.where(Incident.status == status)
        if priority:
            query = query.where(Incident.priority == priority)
        if assigned_to_id:
            query = query.where(Incident.assigned_to_id == assigned_to_id)

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all()
```

### Main Application (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings
from app.core.middleware import TenantMiddleware, AuditLogMiddleware
from app.api.v1 import (
    auth, users, incidents, requests,
    cmdb, knowledge, dashboard
)

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuditLogMiddleware)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(incidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(requests.router, prefix=settings.API_V1_PREFIX)
app.include_router(cmdb.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup():
    # Initialize connections, warm up cache, etc.
    pass

@app.on_event("shutdown")
async def shutdown():
    # Close connections
    pass
```

---

## Frontend Structure Details

### API Client (`src/api/client.ts`)

```typescript
import axios, { AxiosInstance } from 'axios';
import { getAuthToken, refreshToken } from './auth';

const client: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
client.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors and refresh token
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newToken = await refreshToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return client(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default client;
```

### Store (Zustand) (`src/store/authStore.ts`)

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      setAuth: (user, token) => set({ user, token }),
      clearAuth: () => set({ user: null, token: null }),
      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

### Component Example (`src/components/incidents/IncidentCard.tsx`)

```typescript
import React from 'react';
import { Card, Badge, Typography } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { Incident } from '@/types/incident';

interface IncidentCardProps {
  incident: Incident;
  onClick?: (id: string) => void;
}

export const IncidentCard: React.FC<IncidentCardProps> = ({ incident, onClick }) => {
  const priorityColor = {
    critical: 'red',
    high: 'orange',
    medium: 'blue',
    low: 'green',
  }[incident.priority];

  return (
    <Card
      hoverable
      onClick={() => onClick?.(incident.id)}
      className="incident-card"
    >
      <div className="flex justify-between">
        <Typography.Text strong>{incident.ticket_number}</Typography.Text>
        <Badge color={priorityColor} text={incident.priority} />
      </div>
      <Typography.Title level={5}>{incident.title}</Typography.Title>
      <div className="flex items-center text-gray-500">
        <ClockCircleOutlined className="mr-2" />
        <Typography.Text type="secondary">
          {new Date(incident.created_at).toLocaleString()}
        </Typography.Text>
      </div>
    </Card>
  );
};
```

---

## Docker Configuration

### `docker-compose.yml` (Development)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
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
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://opsit:opsit_dev@postgres:5432/opsit_dev
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: dev-secret-key-change-in-production
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://opsit:opsit_dev@postgres:5432/opsit_dev
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/1
      CELERY_RESULT_BACKEND: redis://redis:6379/2
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    command: celery -A app.tasks.celery_app worker --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      VITE_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    command: npm run dev -- --host 0.0.0.0

volumes:
  postgres_data:
  redis_data:
```

---

## Development Workflow

### Initial Setup
```bash
# Clone repository
git clone https://github.com/yourorg/opsit.git
cd opsit

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Seed initial data
docker-compose exec backend python scripts/seed_data.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### Development
```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Run tests
poetry run pytest  # Backend
npm run test       # Frontend
```

---

## Deployment

### Production Build
```bash
# Build Docker images
docker build -t opsit-backend:latest ./backend
docker build -t opsit-frontend:latest ./frontend

# Push to registry
docker push your-registry/opsit-backend:latest
docker push your-registry/opsit-frontend:latest
```

### Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opsit-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: opsit-backend
  template:
    metadata:
      labels:
        app: opsit-backend
    spec:
      containers:
      - name: backend
        image: your-registry/opsit-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: opsit-secrets
              key: database-url
```

---

## Testing Strategy

### Backend Tests
```python
# tests/test_incidents.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/incidents",
        json={
            "title": "Test incident",
            "description": "Test description",
            "urgency": "high",
            "impact": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test incident"
    assert "ticket_number" in data
```

### Frontend Tests
```typescript
// tests/components/IncidentCard.test.tsx
import { render, screen } from '@testing-library/react';
import { IncidentCard } from '@/components/incidents/IncidentCard';

describe('IncidentCard', () => {
  const mockIncident = {
    id: '123',
    ticket_number: 'INC0001234',
    title: 'Test Incident',
    priority: 'high',
    created_at: '2024-01-15T10:00:00Z',
  };

  it('renders incident details', () => {
    render(<IncidentCard incident={mockIncident} />);
    expect(screen.getByText('INC0001234')).toBeInTheDocument();
    expect(screen.getByText('Test Incident')).toBeInTheDocument();
  });
});
```

---

This structure provides:
- ✅ Clear separation of concerns
- ✅ Scalable architecture
- ✅ Easy testing
- ✅ Docker-ready
- ✅ Type-safe (TypeScript + Pydantic)
- ✅ Modern best practices
