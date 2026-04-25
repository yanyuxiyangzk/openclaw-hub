"""add memory column to agents table

Revision ID: 9a7b3c1d_add_memory
Revises: 9a7b3c1d_create_phase5
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a7b3c1d_add_memory'
down_revision: Union[str, None] = '9a7b3c1d_create_phase5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('memory', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'memory')