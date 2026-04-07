"""Script to seed default roles for a tenant"""
import asyncio
import sys
from uuid import UUID
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.core.seed_roles import seed_default_roles


async def main():
    """Seed default roles for all tenants or a specific tenant"""
    async with AsyncSessionLocal() as db:
        # Get all tenants
        stmt = select(Tenant).where(Tenant.is_deleted == False)
        result = await db.execute(stmt)
        tenants = result.scalars().all()

        if not tenants:
            print("No tenants found in database")
            return

        print(f"Found {len(tenants)} tenant(s)")

        for tenant in tenants:
            print(f"\nSeeding roles for tenant: {tenant.name} ({tenant.id})")
            await seed_default_roles(db, tenant.id)

        print("\nAll done!")


if __name__ == "__main__":
    asyncio.run(main())
