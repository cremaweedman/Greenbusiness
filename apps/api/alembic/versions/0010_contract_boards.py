"""contract boards

Revision ID: 0010_contract_boards
Revises: 0009_contract_reputation_rewards
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0010_contract_boards"
down_revision = "0009_contract_reputation_rewards"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "player_contract_boards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("offer_keys", postgresql.JSONB(), nullable=False),
        sa.Column("reroll_count", sa.Integer(), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_player_contract_boards_user_id"),
    )
    op.create_index("ix_player_contract_boards_user_id", "player_contract_boards", ["user_id"], unique=True)


def downgrade():
    op.drop_index("ix_player_contract_boards_user_id", table_name="player_contract_boards")
    op.drop_table("player_contract_boards")
