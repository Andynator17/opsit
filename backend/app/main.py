"""OpsIT FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.api.v1 import auth, users, tasks, categories, support_groups, companies, dashboard, roles, permission_groups, attachments, audit_logs, departments, locations, portals, portal_me, server_scripts, client_scripts, sys_metadata

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Modern ITSM Platform - Made in Europe",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# CORS middleware - use settings with dev fallback
cors_origins = settings.cors_origins or [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to OpsIT API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "status": "operational"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity"""
    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "version": settings.VERSION,
                "database": "connected"
            }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.VERSION,
                "database": "disconnected",
                "error": str(e)
            }
        )


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(companies.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(support_groups.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(roles.router, prefix=settings.API_V1_PREFIX)
app.include_router(permission_groups.router, prefix=settings.API_V1_PREFIX)
app.include_router(attachments.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(departments.router, prefix=settings.API_V1_PREFIX)
app.include_router(locations.router, prefix=settings.API_V1_PREFIX)
app.include_router(portals.router, prefix=settings.API_V1_PREFIX)
app.include_router(portal_me.router, prefix=settings.API_V1_PREFIX)
app.include_router(server_scripts.router, prefix=settings.API_V1_PREFIX)
app.include_router(client_scripts.router, prefix=settings.API_V1_PREFIX)
app.include_router(sys_metadata.router, prefix=settings.API_V1_PREFIX)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"OpsIT API {settings.VERSION} starting...")
    print(f"API Docs: http://localhost:8000{settings.API_V1_PREFIX}/docs")
    print(f"Health Check: http://localhost:8000/health")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("OpsIT API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
