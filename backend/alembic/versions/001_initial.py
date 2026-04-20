"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-04-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('email', sa.String(64), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('avatar', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'organizations',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('owner_id', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
    )

    op.create_table(
        'organization_members',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('org_id', sa.String(64), nullable=False),
        sa.Column('user_id', sa.String(64), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('joined_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )

    op.create_table(
        'invitations',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('org_id', sa.String(64), nullable=False),
        sa.Column('email', sa.String(64), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('token', sa.String(64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_invitations_email', 'invitations', ['email'])


def downgrade() -> None:
    op.drop_index('ix_invitations_email')
    op.drop_table('invitations')
    op.drop_table('organization_members')
    op.drop_table('organizations')
    op.drop_index('ix_users_email')
    op.drop_table('users')
