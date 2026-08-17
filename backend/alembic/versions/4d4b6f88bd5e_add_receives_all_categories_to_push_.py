"""add receives_all_categories to push_subscriptions

Revision ID: 4d4b6f88bd5e
Revises: e3b5aeb687f2
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d4b6f88bd5e'
down_revision: Union[str, None] = 'e3b5aeb687f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'push_subscriptions',
        sa.Column('receives_all_categories', sa.Boolean(), server_default='true', nullable=False),
    )


def downgrade() -> None:
    op.drop_column('push_subscriptions', 'receives_all_categories')
