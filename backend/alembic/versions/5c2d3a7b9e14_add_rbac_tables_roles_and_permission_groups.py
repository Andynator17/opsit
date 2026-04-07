"""Add RBAC tables: roles and permission_groups

Revision ID: 5c2d3a7b9e14
Revises: 4b018309ada7
Create Date: 2026-02-10 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5c2d3a7b9e14'
down_revision: Union[str, None] = '4b018309ada7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table
    op.create_table('roles',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_system_role', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_tenant_id'), 'roles', ['tenant_id'], unique=False)
    op.create_index('ix_roles_code', 'roles', ['code'], unique=False)
    op.create_index('ix_roles_module', 'roles', ['module'], unique=False)

    # Create permission_groups table
    op.create_table('permission_groups',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permission_groups_tenant_id'), 'permission_groups', ['tenant_id'], unique=False)

    # Create permission_group_members association table
    op.create_table('permission_group_members',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('permission_group_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['permission_group_id'], ['permission_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('permission_group_id', 'user_id', name='uq_permission_group_user')
    )
    op.create_index('ix_permission_group_members_group', 'permission_group_members', ['permission_group_id'], unique=False)
    op.create_index('ix_permission_group_members_user', 'permission_group_members', ['user_id'], unique=False)

    # Create permission_group_roles association table
    op.create_table('permission_group_roles',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('permission_group_id', sa.UUID(), nullable=False),
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['permission_group_id'], ['permission_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('permission_group_id', 'role_id', name='uq_permission_group_role')
    )
    op.create_index('ix_permission_group_roles_group', 'permission_group_roles', ['permission_group_id'], unique=False)
    op.create_index('ix_permission_group_roles_role', 'permission_group_roles', ['role_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_permission_group_roles_role', table_name='permission_group_roles')
    op.drop_index('ix_permission_group_roles_group', table_name='permission_group_roles')
    op.drop_table('permission_group_roles')

    op.drop_index('ix_permission_group_members_user', table_name='permission_group_members')
    op.drop_index('ix_permission_group_members_group', table_name='permission_group_members')
    op.drop_table('permission_group_members')

    op.drop_index(op.f('ix_permission_groups_tenant_id'), table_name='permission_groups')
    op.drop_table('permission_groups')

    op.drop_index('ix_roles_module', table_name='roles')
    op.drop_index('ix_roles_code', table_name='roles')
    op.drop_index(op.f('ix_roles_tenant_id'), table_name='roles')
    op.drop_table('roles')
