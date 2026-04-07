"""Add user_type field

Revision ID: 7e8f9a0b13c2
Revises: 6d7e8f9a0b12
Create Date: 2026-02-10 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7e8f9a0b13c2'
down_revision: Union[str, None] = '6d7e8f9a0b12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_type field with default value
    op.add_column('users', sa.Column('user_type', sa.String(length=50), nullable=False, server_default='employee'))


def downgrade() -> None:
    # Drop user_type column
    op.drop_column('users', 'user_type')
