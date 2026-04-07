"""add_work_notes_and_comments_to_tasks

Revision ID: 73ec03b5daa4
Revises: e5b6eb413529
Create Date: 2026-02-10 19:45:44.058579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = '73ec03b5daa4'
down_revision: Union[str, None] = 'e5b6eb413529'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add work_notes and comments JSON columns to tasks table
    op.add_column('tasks', sa.Column('work_notes', JSON, nullable=True))
    op.add_column('tasks', sa.Column('comments', JSON, nullable=True))


def downgrade() -> None:
    # Remove work_notes and comments columns
    op.drop_column('tasks', 'comments')
    op.drop_column('tasks', 'work_notes')
