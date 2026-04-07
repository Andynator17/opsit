"""Seed initial data - tenant, company, admin user"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.company import Company
from app.models.user import User


async def seed_data():
    """Create initial tenant, company, and admin user"""

    async with AsyncSessionLocal() as db:
        try:
            # Check if data already exists
            result = await db.execute(select(Tenant))
            if result.scalar_one_or_none():
                print("Data already seeded!")
                return

            print("Seeding initial data...")

            # Create tenant
            tenant = Tenant(
                name="OpsIT Demo",
                subdomain="demo",
                status="active",
                plan="enterprise",
                max_users=100,
                max_storage_gb=50
            )
            db.add(tenant)
            await db.flush()
            print(f"Created tenant: {tenant.name}")

            # Create company
            company = Company(
                tenant_id=tenant.id,
                name="Demo Company",
                company_code="DEMO",
                company_type="internal",
                status="active",
                primary_email="info@democompany.com",
                city="Berlin",
                country="Germany"
            )
            db.add(company)
            await db.flush()
            print(f"Created company: {company.name}")

            # Create admin user
            admin_user = User(
                tenant_id=tenant.id,
                primary_company_id=company.id,
                user_id="admin",
                email=settings.FIRST_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                first_name="Admin",
                last_name="User",
                job_title="System Administrator",
                is_active=True,
                is_support_agent=True,
                is_admin=True,
                language="en",
                timezone="UTC"
            )
            db.add(admin_user)
            await db.commit()

            print(f"Created admin user: {admin_user.email}")
            print(f"   Password: {settings.FIRST_ADMIN_PASSWORD}")
            print("\nSeed data created successfully!")
            print(f"\nLogin at: http://localhost:8000{settings.API_V1_PREFIX}/docs")
            print(f"   Email: {settings.FIRST_ADMIN_EMAIL}")
            print(f"   Password: {settings.FIRST_ADMIN_PASSWORD}")

        except Exception as e:
            print(f"Error seeding data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    print("Starting seed script...")
    asyncio.run(seed_data())
