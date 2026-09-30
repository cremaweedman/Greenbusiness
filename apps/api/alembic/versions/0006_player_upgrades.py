"""player upgrades

Revision ID: 0006_player_upgrades
Revises: 0005_contracts_economy
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_player_upgrades"
down_revision = "0005_contracts_economy"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "player_upgrades",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("upgrade_key", sa.String(96), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "upgrade_key", name="uq_player_upgrade_user_key"),
    )
    op.create_index("ix_player_upgrades_user_id", "player_upgrades", ["user_id"])


def downgrade():
    op.drop_index("ix_player_upgrades_user_id", table_name="player_upgrades")
    op.drop_table("player_upgrades")
