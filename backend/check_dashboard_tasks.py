"""
Check what tasks should be shown in dashboard
"""
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.task import Task
from app.models.support_group import SupportGroup


async def check_dashboard_tasks():
    """Check tasks"""
    async with AsyncSessionLocal() as session:
        print("=" * 60)
        print("DASHBOARD TASKS CHECK")
        print("=" * 60)
        print()

        # Get Servicedesk group ID
        group_result = await session.execute(
            select(SupportGroup).where(
                SupportGroup.name == "Servicedesk",
                SupportGroup.is_deleted == False
            )
        )
        servicedesk_group = group_result.scalar_one_or_none()

        if not servicedesk_group:
            print("ERROR: Servicedesk group not found!")
            return

        print(f"Servicedesk Group ID: {servicedesk_group.id}\n")

        # Get all active tasks assigned to Servicedesk
        tasks_result = await session.execute(
            select(Task).where(
                Task.assignment_group_id == servicedesk_group.id,
                Task.is_deleted == False
            ).order_by(Task.sys_created_on.desc())
        )
        tasks = tasks_result.scalars().all()

        print(f"Total tasks assigned to Servicedesk: {len(tasks)}\n")

        for task in tasks:
            closed_statuses = ['resolved', 'closed', 'cancelled', 'fulfilled']
            is_closed = task.status in closed_statuses
            print(f"Number: {task.number}")
            print(f"  Type: {task.sys_class_name}")
            print(f"  Status: {task.status} {'(CLOSED - will NOT show in dashboard)' if is_closed else '(OPEN - WILL show in dashboard)'}")
            print(f"  Priority: {task.priority}")
            print(f"  Title: {task.short_description[:50]}")
            print(f"  Created: {task.sys_created_on}")
            print()


if __name__ == "__main__":
    asyncio.run(check_dashboard_tasks())
