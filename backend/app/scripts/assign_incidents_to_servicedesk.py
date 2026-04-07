"""
Assign all open incidents to the Servicedesk support group.

Usage:
    python -m app.scripts.assign_incidents_to_servicedesk
"""
import asyncio
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.support_group import SupportGroup
from app.models.incident import Incident


async def assign_open_incidents_to_servicedesk():
    """Assign all open incidents to Servicedesk support group"""
    async with AsyncSessionLocal() as session:
        # Find Servicedesk support group
        result = await session.execute(
            select(SupportGroup).where(
                SupportGroup.name == "Servicedesk",
                SupportGroup.is_deleted == False,
            )
        )
        servicedesk_group = result.scalar_one_or_none()

        if not servicedesk_group:
            print("ERROR: Servicedesk support group not found!")
            print("Please create the Servicedesk support group first.")
            return

        print(f"Found Servicedesk group: {servicedesk_group.name} (ID: {servicedesk_group.id})")
        print(f"Tenant: {servicedesk_group.tenant_id}")

        # Define open statuses
        open_statuses = ["new", "assigned", "in_progress", "pending"]

        # Find all open incidents without an assigned group
        result = await session.execute(
            select(Incident).where(
                Incident.tenant_id == servicedesk_group.tenant_id,
                Incident.status.in_(open_statuses),
                Incident.assigned_group_id.is_(None),
                Incident.is_deleted == False,
            )
        )
        open_incidents = result.scalars().all()

        if not open_incidents:
            print("\nNo open incidents found without an assigned group.")
            return

        print(f"\nFound {len(open_incidents)} open incident(s) without assigned group:")
        for incident in open_incidents:
            print(f"  - {incident.incident_number}: {incident.title} (Status: {incident.status})")

        # Assign all to Servicedesk
        for incident in open_incidents:
            incident.assigned_group_id = servicedesk_group.id
            # If status is "new", update to "assigned"
            if incident.status == "new":
                incident.status = "assigned"

        await session.commit()

        print(f"\nSuccessfully assigned {len(open_incidents)} incident(s) to Servicedesk support group!")
        print("Incidents with status 'new' have been updated to 'assigned'.")


if __name__ == "__main__":
    print("Starting incident assignment to Servicedesk...\n")
    asyncio.run(assign_open_incidents_to_servicedesk())
