"""Add extended user fields

Revision ID: 6d7e8f9a0b12
Revises: 5c2d3a7b9e14
Create Date: 2026-02-10 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6d7e8f9a0b12'
down_revision: Union[str, None] = '5c2d3a7b9e14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new user fields
    # Make user_id unique
    op.create_unique_constraint('uq_users_user_id', 'users', ['user_id'])

    # Add secondary email
    op.add_column('users', sa.Column('email_secondary', sa.String(length=255), nullable=True))

    # Add employee ID
    op.add_column('users', sa.Column('employee_id', sa.String(length=50), nullable=True))
    op.create_index('ix_users_employee_id', 'users', ['employee_id'], unique=False)

    # Add personal details
    op.add_column('users', sa.Column('salutation', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('title', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('middle_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))

    # Add secondary phone
    op.add_column('users', sa.Column('phone_secondary', sa.String(length=50), nullable=True))

    # Add work information
    op.add_column('users', sa.Column('department', sa.String(length=100), nullable=True))
    op.create_index('ix_users_department', 'users', ['department'], unique=False)

    op.add_column('users', sa.Column('location', sa.String(length=100), nullable=True))
    op.create_index('ix_users_location', 'users', ['location'], unique=False)


def downgrade() -> None:
    # Drop columns in reverse order
    op.drop_index('ix_users_location', table_name='users')
    op.drop_column('users', 'location')

    op.drop_index('ix_users_department', table_name='users')
    op.drop_column('users', 'department')

    op.drop_column('users', 'phone_secondary')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'middle_name')
    op.drop_column('users', 'title')
    op.drop_column('users', 'salutation')

    op.drop_index('ix_users_employee_id', table_name='users')
    op.drop_column('users', 'employee_id')

    op.drop_column('users', 'email_secondary')

    op.drop_constraint('uq_users_user_id', 'users', type_='unique')
