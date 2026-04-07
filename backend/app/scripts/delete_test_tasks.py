"""
Delete test tasks
"""
import asyncio
from sqlalchemy import select, delete

from app.core.database import AsyncSessionLocal
from app.models.task import Task


async def delete_test_tasks():
    """Delete test tasks"""
    async with AsyncSessionLocal() as session:
        # Delete by number
        test_numbers = [
            'INC000000004',
            'REQ000000001',
            'CHG000000001',
            'PRB000000001',
            'TASK000000001',
            'APPR000000001'
        ]

        result = await session.execute(
            delete(Task).where(Task.number.in_(test_numbers))
        )

        await session.commit()
        print(f"Deleted {result.rowcount} test tasks")


if __name__ == "__main__":
    asyncio.run(delete_test_tasks())
