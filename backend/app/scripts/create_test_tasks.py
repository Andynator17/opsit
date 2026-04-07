"""
Create test tasks for all ticket types
"""
import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.task import Task
from app.models.support_group import SupportGroup


async def create_test_tasks():
    """Create test tasks for all ticket types"""
    async with AsyncSessionLocal() as session:
        print("=" * 60)
        print("CREATE TEST TASKS")
        print("=" * 60)
        print()

        # Find admin user and company
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

        print(f"User: {admin_user.email} (ID: {admin_user.id})")
        print(f"Tenant: {admin_user.tenant_id}")
        print(f"Company: {admin_user.primary_company_id}")

        # Find Servicedesk support group
        group_result = await session.execute(
            select(SupportGroup).where(
                SupportGroup.name == "Servicedesk",
                SupportGroup.tenant_id == admin_user.tenant_id,
                SupportGroup.is_deleted == False
            )
        )
        servicedesk_group = group_result.scalar_one_or_none()

        if not servicedesk_group:
            print("ERROR: Servicedesk support group not found!")
            return

        print(f"Support Group: {servicedesk_group.name} (ID: {servicedesk_group.id})\n")

        # Test data for each ticket type
        test_tasks = [
            {
                "sys_class_name": "incident",
                "short_description": "Server down - Production database not responding",
                "description": "The production database server is not responding. Multiple users are affected and cannot access the application.",
                "urgency": "critical",
                "impact": "high",
                "category": "Software",
            },
            {
                "sys_class_name": "request",
                "short_description": "Request new laptop for new employee",
                "description": "New employee John Doe starts next Monday. Please provide a standard developer laptop with Windows 11 and required software.",
                "urgency": "medium",
                "impact": "low",
                "category": "Hardware",
            },
            {
                "sys_class_name": "change",
                "short_description": "Upgrade database server to PostgreSQL 16",
                "description": "Plan and execute upgrade of production database from PostgreSQL 15 to PostgreSQL 16. Requires downtime window and rollback plan.",
                "urgency": "low",
                "impact": "high",
                "category": "Software",
            },
            {
                "sys_class_name": "problem",
                "short_description": "Recurring network timeouts during peak hours",
                "description": "Users experience network timeouts every day between 2-4 PM. Multiple incidents have been created. Root cause analysis needed.",
                "urgency": "high",
                "impact": "medium",
                "category": "Network",
            },
            {
                "sys_class_name": "task",
                "short_description": "Update firewall rules for new application",
                "description": "Configure firewall to allow traffic for new web application on ports 8080 and 8443.",
                "urgency": "medium",
                "impact": "medium",
                "category": "Network",
            },
            {
                "sys_class_name": "approval",
                "short_description": "Approval request for software license purchase",
                "description": "Requesting approval to purchase 10 additional Jira licenses for the development team. Total cost: EUR 5,000/year.",
                "urgency": "medium",
                "impact": "low",
                "category": "Other",
            },
        ]

        created_count = 0

        for task_data in test_tasks:
            # Calculate priority
            priority = Task.calculate_priority(task_data["urgency"], task_data["impact"])

            # Get prefix and generate number
            prefix = Task.get_prefix_for_class(task_data["sys_class_name"])

            # Get count for this type
            count_result = await session.execute(
                select(Task).where(
                    Task.sys_class_name == task_data["sys_class_name"],
                    Task.tenant_id == admin_user.tenant_id
                )
            )
            existing_count = len(count_result.scalars().all())
            sequence = existing_count + 1

            ticket_number = Task.generate_number(prefix, sequence)

            # Determine initial status
            status_map = {
                "incident": "new",
                "request": "submitted",
                "change": "draft",
                "problem": "new",
                "task": "pending",
                "approval": "pending",
            }
            initial_status = status_map.get(task_data["sys_class_name"], "new")

            # Create task
            task = Task(
                sys_id=uuid.uuid4(),
                number=ticket_number,
                sys_class_name=task_data["sys_class_name"],
                tenant_id=admin_user.tenant_id,
                company_id=admin_user.primary_company_id,
                short_description=task_data["short_description"],
                description=task_data["description"],
                category=task_data["category"],
                urgency=task_data["urgency"],
                impact=task_data["impact"],
                priority=priority,
                status=initial_status,
                channel="web",
                opened_by_id=admin_user.id,
                assignment_group_id=servicedesk_group.id,  # Assign to Servicedesk
                is_active=True,
                is_deleted=False,
            )

            session.add(task)
            print(f"OK Created: {ticket_number} - {task_data['short_description'][:50]}...")
            created_count += 1

        # Commit all
        await session.commit()

        print("\n" + "=" * 60)
        print(f"Successfully created {created_count} test tasks!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_test_tasks())
