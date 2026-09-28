"""foundation

Revision ID: 0001_foundation
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "app_meta",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", sa.String(255), nullable=False),
    )


def downgrade():
    op.drop_table("app_meta")
