"""add_activity_read_at

Revision ID: 2026_04_26_0001
Revises:
Create Date: 2026-04-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_04_26_0001'
down_revision = '9a7b3c1d_add_memory'  # Adjust based on your current head
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('activities', sa.Column('read_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('activities', 'read_at')