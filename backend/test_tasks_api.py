"""
Test tasks API endpoint
"""
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.task import Task
from app.models.support_group import SupportGroup, group_members
from app.models.user import User


async def test_tasks_api():
    """Test if tasks are returned correctly"""
    async with AsyncSessionLocal() as session:
        print("=" * 60)
        print("TEST TASKS API")
        print("=" * 60)
        print()

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

        print(f"Admin User: {admin_user.email} (ID: {admin_user.id})")
        print(f"Tenant: {admin_user.tenant_id}\n")

        # Get user's support groups
        group_result = await session.execute(
            select(group_members.c.group_id).where(
                group_members.c.user_id == admin_user.id
            )
        )
        user_group_ids = [row[0] for row in group_result.all()]
        print(f"User's Support Groups: {user_group_ids}\n")

        # Get all tasks for this tenant
        tasks_result = await session.execute(
            select(Task).where(
                Task.tenant_id == admin_user.tenant_id,
                Task.is_deleted == False
            )
        )
        all_tasks = tasks_result.scalars().all()

        print(f"Total Tasks in Database: {len(all_tasks)}")
        for task in all_tasks:
            print(f"  - {task.number} ({task.sys_class_name}): {task.short_description[:50]}")
            print(f"    Assignment Group: {task.assignment_group_id}")
            print(f"    Status: {task.status}")
            print()

        # Get tasks assigned to user's groups (simulating the API filter)
        if user_group_ids:
            filtered_result = await session.execute(
                select(Task).where(
                    Task.tenant_id == admin_user.tenant_id,
                    Task.assignment_group_id.in_(user_group_ids),
                    Task.is_deleted == False
                )
            )
            filtered_tasks = filtered_result.scalars().all()

            print(f"Tasks Assigned to User's Groups: {len(filtered_tasks)}")
            for task in filtered_tasks:
                print(f"  - {task.number} ({task.sys_class_name}): {task.short_description[:50]}")
        else:
            print("User is not in any support groups!")


if __name__ == "__main__":
    asyncio.run(test_tasks_api())
