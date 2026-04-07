"""
Test script to verify incident filtering by support groups
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.incident import Incident
from app.models.support_group import group_members


async def test_incident_filter():
    """Test the assigned_to_my_groups filter logic"""
    async with AsyncSessionLocal() as session:
        # Find admin user
        result = await session.execute(
            select(User).where(
                User.email == "admin@opsit.com",
                User.is_deleted == False
            )
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            print("ERROR: Admin user not found!")
            return

        print(f"Found user: {admin_user.email} (ID: {admin_user.id})")
        print(f"Tenant: {admin_user.tenant_id}\n")

        # Get user's support groups
        group_result = await session.execute(
            select(group_members.c.group_id).where(
                group_members.c.user_id == admin_user.id
            )
        )
        user_group_ids = [row[0] for row in group_result.all()]

        print(f"User is member of {len(user_group_ids)} support group(s):")
        for group_id in user_group_ids:
            print(f"  - Group ID: {group_id}")

        if not user_group_ids:
            print("\nWARNING: User is not a member of any support groups!")
            return

        print("\n" + "="*60)

        # Query incidents assigned to these groups
        query = select(Incident).where(
            Incident.tenant_id == admin_user.tenant_id,
            Incident.assigned_group_id.in_(user_group_ids),
            Incident.is_deleted == False
        )

        incidents_result = await session.execute(query)
        incidents = incidents_result.scalars().all()

        print(f"\nIncidents assigned to user's support groups: {len(incidents)}")
        for incident in incidents:
            print(f"  - {incident.incident_number}: {incident.title}")
            print(f"    Status: {incident.status}")
            print(f"    Assigned Group ID: {incident.assigned_group_id}")
            print()

        # Also query ALL incidents for comparison
        all_incidents_result = await session.execute(
            select(Incident).where(
                Incident.tenant_id == admin_user.tenant_id,
                Incident.is_deleted == False
            )
        )
        all_incidents = all_incidents_result.scalars().all()

        print(f"Total incidents in tenant: {len(all_incidents)}")
        for incident in all_incidents:
            print(f"  - {incident.incident_number}: {incident.title}")
            print(f"    Status: {incident.status}")
            print(f"    Assigned Group ID: {incident.assigned_group_id}")
            print()


if __name__ == "__main__":
    print("Testing incident filter by support groups...\n")
    asyncio.run(test_incident_filter())
