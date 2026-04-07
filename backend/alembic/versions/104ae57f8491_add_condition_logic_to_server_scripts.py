"""add_condition_logic_to_server_scripts

Revision ID: 104ae57f8491
Revises: fdeb64d4a1d4
Create Date: 2026-02-11 18:16:54.520368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '104ae57f8491'
down_revision: Union[str, None] = 'fdeb64d4a1d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('server_scripts', sa.Column('condition_logic', sa.String(length=10), nullable=False, server_default='and'))


def downgrade() -> None:
    op.drop_column('server_scripts', 'condition_logic')
