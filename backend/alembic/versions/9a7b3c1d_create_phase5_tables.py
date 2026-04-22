"""create executions scheduler_jobs workflows tables

Revision ID: 9a7b3c1d_create_phase5
Revises: 9a7b3c1d_create_tasks
Create Date: 2026-04-23 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a7b3c1d_create_phase5'
down_revision: Union[str, None] = '9a7b3c1d_create_tasks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('executions',
    sa.Column('id', sa.TEXT(), nullable=False),
    sa.Column('task_id', sa.TEXT(), nullable=False),
    sa.Column('agent_id', sa.TEXT(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('input_data', sa.Text(), nullable=True),
    sa.Column('output_data', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scheduler_jobs',
    sa.Column('id', sa.TEXT(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('task_template_id', sa.TEXT(), nullable=False),
    sa.Column('cron_expression', sa.String(length=64), nullable=False),
    sa.Column('agent_id', sa.TEXT(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('last_run_at', sa.DateTime(), nullable=True),
    sa.Column('next_run_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_template_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('workflows',
    sa.Column('id', sa.TEXT(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('steps', sa.Text(), nullable=False),
    sa.Column('org_id', sa.TEXT(), nullable=False),
    sa.Column('created_by', sa.TEXT(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('workflows')
    op.drop_table('scheduler_jobs')
    op.drop_table('executions')
