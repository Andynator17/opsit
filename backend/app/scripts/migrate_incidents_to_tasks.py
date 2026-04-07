"""
Migration script: Migrate existing incidents to the new tasks table
"""
import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.incident import Incident
from app.models.task import Task


async def migrate_incidents_to_tasks():
    """Migrate all incidents from incidents table to tasks table"""
    async with AsyncSessionLocal() as session:
        print("Starting migration: Incidents -> Tasks\n")
        print("=" * 60)

        # Fetch all incidents
        result = await session.execute(
            select(Incident).where(Incident.is_deleted == False)
        )
        incidents = result.scalars().all()

        print(f"Found {len(incidents)} incidents to migrate\n")

        migrated_count = 0
        skipped_count = 0

        for incident in incidents:
            # Check if already migrated (by incident_number)
            existing = await session.execute(
                select(Task).where(Task.number == incident.incident_number)
            )
            if existing.scalar_one_or_none():
                print(f">> Skipping {incident.incident_number} - already migrated")
                skipped_count += 1
                continue

            # Map incident fields to task fields
            task = Task(
                # System fields
                sys_id=uuid.uuid4(),
                number=incident.incident_number,
                sys_class_name="incident",
                sys_created_on=incident.created_at,
                sys_updated_on=incident.updated_at or incident.created_at,

                # Multi-tenancy
                tenant_id=incident.tenant_id,

                # Basic information
                short_description=incident.title,
                description=incident.description,

                # Company & User fields
                company_id=incident.company_id,
                opened_by_id=incident.opened_by_id or incident.reported_by_id,  # Use opened_by or fallback to reported_by
                caller_id=incident.caller_id,
                caller_company_id=None,  # Not in old model
                affected_user_id=incident.affected_user_id,
                affected_user_company_id=None,  # Not in old model

                # Assignment
                assignment_group_id=incident.assigned_group_id,
                assigned_to_id=incident.assigned_to_id,
                reassignment_count=0,  # Not tracked in old model

                # Categorization
                category=incident.category,
                subcategory=incident.subcategory,
                service_id=None,  # Not in old model
                channel=incident.contact_type or "web",

                # Priority matrix
                impact=incident.impact,
                urgency=incident.urgency,
                priority=incident.priority,

                # Status
                status=incident.status,
                status_reason=incident.status_reason,

                # Resolution
                resolved_by_id=incident.resolved_by_id,
                resolved_at=incident.resolved_date,
                resolution=incident.resolution_notes,
                resolution_reason=incident.resolution_code,
                close_notes=None,  # Not in old model
                closed_by_id=incident.closed_by_id,
                closed_at=incident.closed_date,

                # SLA
                sla_target_respond=incident.sla_target_respond,
                sla_target_resolve=incident.sla_target_resolve,
                sla_breach=bool(incident.sla_breach) if incident.sla_breach is not None else False,
                response_time_minutes=incident.response_time_minutes,
                resolution_time_minutes=incident.resolution_time_minutes,

                # Audit
                last_modified_by_id=None,  # Not in old model
                last_modified_at=incident.updated_at or incident.created_at,

                # Additional details
                additional_comments=None,
                root_cause=incident.root_cause,
                workaround=incident.workaround,
                affected_services=incident.affected_services,
                affected_users_count=incident.affected_users_count or 1,

                # External references
                parent_task_id=None,
                related_task_id=None,
                external_ticket_id=incident.external_ticket_id,

                # Custom fields
                custom_fields=incident.custom_fields,
                contact_type=incident.contact_type,

                # Base fields
                is_active=bool(incident.is_active) if incident.is_active is not None else True,
                is_deleted=bool(incident.is_deleted) if incident.is_deleted is not None else False,
                deleted_at=incident.deleted_at,
                created_at=incident.created_at,
                updated_at=incident.updated_at or incident.created_at,
            )

            session.add(task)
            print(f"OK Migrated: {incident.incident_number} - {incident.title}")
            migrated_count += 1

        # Commit all migrations
        await session.commit()

        print("\n" + "=" * 60)
        print(f"Migration completed!")
        print(f"  OK Migrated: {migrated_count}")
        print(f"  >> Skipped:  {skipped_count}")
        print(f"  ## Total:    {len(incidents)}")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("INCIDENT -> TASK MIGRATION")
    print("=" * 60)
    print()
    asyncio.run(migrate_incidents_to_tasks())
